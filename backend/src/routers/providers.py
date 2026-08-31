from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session, select
import logging
from src.database import get_session
from src.models.models import User, Provider, ProviderContact, ProviderStatus
from src.schemas.schemas import (
    ProviderCreate, ProviderResponse, ProviderUpdate,
    ProviderDeleteResponse, ProviderContactCreate,
    ProviderContactResponse, ProviderContactUpdate,
    BulkImportResult,
)
from src.dependencies import get_current_user
from src.bulk.parser import (
    RowError,
    name_key,
    optional_text,
    parse_spreadsheet,
    required_raw,
    run_bulk,
    template_response,
)
from datetime import datetime, timezone

router = APIRouter(prefix="/providers", tags=["Providers"])

# ── POST /providers/ ────────────────────────────────────────────────────────
@router.post(
    "/",
    response_model=ProviderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo proveedor",
)
def create_provider(
    provider_data: ProviderCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    existing_nit = session.exec(
        select(Provider).where(Provider.nit == provider_data.nit)
    ).first()
    if existing_nit:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un proveedor con el NIT '{provider_data.nit}'.",
        )

    existing_email = session.exec(
        select(Provider).where(Provider.email == provider_data.email)
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un proveedor con el email '{provider_data.email}'.",
        )

    new_provider = Provider(
        **provider_data.model_dump(),
        created_by=current_user.id,
    )
    session.add(new_provider)
    session.commit()
    session.refresh(new_provider)
    return new_provider


# ── GET /providers/ ─────────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=list[ProviderResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los proveedores",
)
def get_all_providers(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    providers = session.exec(select(Provider)).all()
    return providers


# ── GET /providers/{provider_id} ─────────────────────────────────────────────
@router.get(
    "/{provider_id}",
    response_model=ProviderResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener proveedor por ID con sus contactos",
)
def get_provider(
    provider_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    provider = session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El proveedor con id '{provider_id}' no existe.",
        )
    return provider


# ── PATCH /providers/{provider_id} ──────────────────────────────────────────
@router.patch(
    "/{provider_id}",
    response_model=ProviderResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar proveedor parcialmente",
)
def update_provider(
    provider_id: int,
    provider_data: ProviderUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    provider = session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El proveedor con id '{provider_id}' no existe.",
        )
    if provider.status == ProviderStatus.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El proveedor con id '{provider_id}' está inactivo.",
        )

    if provider_data.nit and provider_data.nit != provider.nit:
        existing = session.exec(
            select(Provider).where(Provider.nit == provider_data.nit)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un proveedor con el NIT '{provider_data.nit}'.",
            )

    if provider_data.email and provider_data.email != provider.email:
        existing = session.exec(
            select(Provider).where(Provider.email == provider_data.email)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un proveedor con el email '{provider_data.email}'.",
            )

    update_data = provider_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(provider, field, value)

    provider.updated_at = datetime.now(timezone.utc)
    provider.updated_by = current_user.id

    session.add(provider)
    session.commit()
    session.refresh(provider)
    return provider


# ── DELETE /providers/{provider_id} ─────────────────────────────────────────
@router.delete(
    "/{provider_id}",
    response_model=ProviderDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar proveedor (soft delete)",
)
def delete_provider(
    provider_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    provider = session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El proveedor con id '{provider_id}' no existe.",
        )
    if provider.status == ProviderStatus.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El proveedor con id '{provider_id}' ya fue eliminado.",
        )

    now = datetime.now(timezone.utc)
    provider.deleted_at = now
    provider.deleted_by = current_user.id
    provider.status = ProviderStatus.INACTIVE

    session.add(provider)
    session.commit()

    return ProviderDeleteResponse(
        message=f"Proveedor '{provider.company}' eliminado correctamente.",
        deleted_at=now,
        deleted_by=current_user.id,
    )


# ════════════════════════════════════════════════════════════════════════════
# CONTACTS
# ════════════════════════════════════════════════════════════════════════════

# ── POST /providers/{provider_id}/contacts/ ──────────────────────────────────
@router.post(
    "/{provider_id}/contacts/",
    response_model=ProviderContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar contacto a un proveedor",
)
def create_contact(
    provider_id: int,
    contact_data: ProviderContactCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    provider = session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El proveedor con id '{provider_id}' no existe.",
        )
    if provider.status == ProviderStatus.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pueden agregar contactos a un proveedor inactivo.",
        )

    new_contact = ProviderContact(
        **contact_data.model_dump(),
        provider_id=provider_id,
        created_by=current_user.id,
    )
    session.add(new_contact)
    session.commit()
    session.refresh(new_contact)
    return new_contact


# ── PATCH /providers/{provider_id}/contacts/{contact_id} ────────────────────
@router.patch(
    "/{provider_id}/contacts/{contact_id}",
    response_model=ProviderContactResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar contacto de un proveedor",
)
def update_contact(
    provider_id: int,
    contact_id: int,
    contact_data: ProviderContactUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    provider = session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El proveedor con id '{provider_id}' no existe.",
        )

    contact = session.get(ProviderContact, contact_id)
    if not contact or contact.provider_id != provider_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El contacto con id '{contact_id}' no existe en este proveedor.",
        )
    if contact.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El contacto con id '{contact_id}' está eliminado.",
        )

    update_data = contact_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)

    contact.updated_at = datetime.now(timezone.utc)
    contact.updated_by = current_user.id

    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact


# ── DELETE /providers/{provider_id}/contacts/{contact_id} ───────────────────
@router.delete(
    "/{provider_id}/contacts/{contact_id}",
    response_model=ProviderDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar contacto de un proveedor (soft delete)",
)
def delete_contact(
    provider_id: int,
    contact_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    provider = session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El proveedor con id '{provider_id}' no existe.",
        )

    contact = session.get(ProviderContact, contact_id)
    if not contact or contact.provider_id != provider_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El contacto con id '{contact_id}' no existe en este proveedor.",
        )
    if contact.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El contacto con id '{contact_id}' ya fue eliminado.",
        )

    now = datetime.now(timezone.utc)
    contact.deleted_at = now
    contact.deleted_by = current_user.id

    session.add(contact)
    session.commit()

    return ProviderDeleteResponse(
        message=f"Contacto '{contact.name}' eliminado correctamente.",
        deleted_at=now,
        deleted_by=current_user.id,
    )


# ════════════════════════════════════════════════════════════════════════════
# CARGA MASIVA
# ════════════════════════════════════════════════════════════════════════════

BULK_PROVIDER_HEADERS = ["empresa", "nit", "email"]
BULK_PROVIDER_EXAMPLES = [["Distribuidora del Campo SAS", "900123456-7", "ventas@distribuidoracampo.com"]]

BULK_CONTACT_HEADERS = ["empresa_proveedor", "nombre", "email", "telefono", "notas"]
BULK_CONTACT_EXAMPLES = [["Distribuidora del Campo SAS", "Carlos Martinez", "carlos@distribuidoracampo.com", "3001234567", "Contacto principal"]]


def _valid_email(value: str) -> str:
    if len(value) > 150 or "@" not in value or value.startswith("@"):
        raise RowError(f"Email inválido: '{value}'")
    return value


@router.post(
    "/bulk/import",
    response_model=BulkImportResult,
    status_code=status.HTTP_200_OK,
    summary="Cargar proveedores por archivo Excel/CSV",
)
def bulk_import_providers(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    rows = parse_spreadsheet(file)
    seen_nit = set()
    seen_email = set()

    def process_row(row):
        empresa = required_raw(row, "empresa", "empresa")
        if len(empresa) > 150:
            raise RowError("La empresa supera los 150 caracteres.")
        nit = required_raw(row, "nit", "nit")
        if len(nit) > 20:
            raise RowError("El NIT supera los 20 caracteres.")
        email = _valid_email(str(row.get("email") or "").strip().lower())

        if nit in seen_nit:
            raise RowError(f"El NIT '{row.get('nit')}' ya aparece en otra fila del archivo.")
        if email and email in seen_email:
            raise RowError(f"El email '{row.get('email')}' ya aparece en otra fila del archivo.")

        if session.exec(select(Provider).where(Provider.nit == nit)).first():
            raise RowError(f"Ya existe un proveedor con el NIT '{row.get('nit')}'.")
        if email and session.exec(select(Provider).where(Provider.email == email)).first():
            raise RowError(f"Ya existe un proveedor con el email '{row.get('email')}'.")

        seen_nit.add(nit)
        if email:
            seen_email.add(email)

        session.add(Provider(
            company=empresa,
            nit=nit,
            email=email,
            created_by=current_user.id,
        ))
        return False

    return run_bulk(session, rows, process_row)


@router.get(
    "/bulk/template",
    status_code=status.HTTP_200_OK,
    summary="Descargar plantilla de proveedores",
)
def bulk_providers_template():
    return template_response(
        "plantilla_proveedores.xlsx", BULK_PROVIDER_HEADERS, BULK_PROVIDER_EXAMPLES
    )


@router.post(
    "/contacts/bulk/import",
    response_model=BulkImportResult,
    status_code=status.HTTP_200_OK,
    summary="Cargar contactos de proveedores por archivo Excel/CSV",
)
def bulk_import_provider_contacts(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    rows = parse_spreadsheet(file)
    providers = {
        name_key(p.company): p
        for p in session.exec(select(Provider)).all()
        if p.deleted_at is None and p.status == ProviderStatus.ACTIVE
    }

    def process_row(row):
        empresa = required_raw(row, "empresa_proveedor", "empresa_proveedor")
        provider = providers.get(name_key(empresa))
        if provider is None:
            raise RowError(f"No existe el proveedor '{row.get('empresa_proveedor')}'.")

        nombre = required_raw(row, "nombre", "nombre")
        if len(nombre) > 150:
            raise RowError("El nombre del contacto supera los 150 caracteres.")

        email = str(row.get("email") or "").strip().lower()
        if email:
            _valid_email(email)

        telefono = row.get("telefono")
        if telefono is not None and len(str(telefono).strip()) > 20:
            raise RowError("El teléfono supera los 20 caracteres.")

        session.add(ProviderContact(
            provider_id=provider.id,
            name=nombre,
            email=email or None,
            phone=str(telefono).strip() if telefono is not None and str(telefono).strip() else None,
            notes=optional_text(row, "notas"),
            created_by=current_user.id,
        ))
        return False

    return run_bulk(session, rows, process_row)


@router.get(
    "/contacts/bulk/template",
    status_code=status.HTTP_200_OK,
    summary="Descargar plantilla de contactos de proveedores",
)
def bulk_provider_contacts_template():
    return template_response(
        "plantilla_contactos_proveedores.xlsx", BULK_CONTACT_HEADERS, BULK_CONTACT_EXAMPLES
    )
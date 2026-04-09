from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
import logging
from src.database import get_session
from src.models.models import User, Provider, ProviderContact, ProviderStatus
from src.schemas.schemas import (
    ProviderCreate, ProviderResponse, ProviderUpdate,
    ProviderDeleteResponse, ProviderContactCreate,
    ProviderContactResponse, ProviderContactUpdate,
)
from src.dependencies import get_current_user
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
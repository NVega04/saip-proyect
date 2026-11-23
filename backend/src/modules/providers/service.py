from datetime import datetime, timezone

from sqlmodel import Session, select

from src.bulk.parser import (
    RowError,
    name_key,
    optional_text,
    parse_spreadsheet,
    required_raw,
    run_bulk,
)
from src.core.crypto import blind_index
from src.core.exceptions import ConflictError, NotFoundError
from src.core.schemas import BulkImportResult
from src.modules.providers.models import Provider, ProviderContact, ProviderStatus
from src.modules.providers.schemas import (
    ProviderContactCreate,
    ProviderContactUpdate,
    ProviderCreate,
    ProviderDeleteResponse,
    ProviderUpdate,
)
from src.modules.users.models import User

BULK_PROVIDER_HEADERS = ["empresa", "nit", "email"]
BULK_PROVIDER_EXAMPLES = [
    [
        "Distribuidora del Campo SAS",
        "900123456-7",
        "ventas@distribuidoracampo.com",
    ]
]

BULK_CONTACT_HEADERS = ["empresa_proveedor", "nombre", "email", "telefono", "notas"]
BULK_CONTACT_EXAMPLES = [
    [
        "Distribuidora del Campo SAS",
        "Carlos Martinez",
        "carlos@distribuidoracampo.com",
        "3001234567",
        "Contacto principal",
    ]
]


def _valid_email(value: str) -> str:
    if len(value) > 150 or "@" not in value or value.startswith("@"):
        raise RowError(f"Email inválido: '{value}'")
    return value


class ProvidersService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: ProviderCreate, current_user: User) -> Provider:
        existing_nit = self.session.exec(
            select(Provider).where(Provider.nit_hash == blind_index(data.nit))
        ).first()
        if existing_nit:
            raise ConflictError(
                f"Ya existe un proveedor con el NIT '{data.nit}'."
            )

        existing_email = self.session.exec(
            select(Provider).where(Provider.email == data.email)
        ).first()
        if existing_email:
            raise ConflictError(
                f"Ya existe un proveedor con el email '{data.email}'."
            )

        new_provider = Provider(
            **data.model_dump(),
            created_by=current_user.id,
        )
        self.session.add(new_provider)
        self.session.commit()
        self.session.refresh(new_provider)
        return new_provider

    def list(self, skip: int = 0, limit: int = 20) -> list[Provider]:
        return self.session.exec(select(Provider).offset(skip).limit(limit)).all()

    def get(self, provider_id: int) -> Provider:
        provider = self.session.get(Provider, provider_id)
        if not provider:
            raise NotFoundError(
                f"El proveedor con id '{provider_id}' no existe."
            )
        return provider

    def update(
        self, provider_id: int, data: ProviderUpdate, current_user: User
    ) -> Provider:
        provider = self.get(provider_id)
        if provider.status == ProviderStatus.INACTIVE:
            raise ConflictError(
                f"El proveedor con id '{provider_id}' está inactivo."
            )

        if data.nit and data.nit != provider.nit:
            existing = self.session.exec(
                select(Provider).where(Provider.nit_hash == blind_index(data.nit))
            ).first()
            if existing:
                raise ConflictError(
                    f"Ya existe un proveedor con el NIT '{data.nit}'."
                )

        if data.email and data.email != provider.email:
            existing = self.session.exec(
                select(Provider).where(Provider.email == data.email)
            ).first()
            if existing:
                raise ConflictError(
                    f"Ya existe un proveedor con el email '{data.email}'."
                )

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(provider, field, value)
        if data.nit:
            provider.nit_hash = blind_index(data.nit)

        provider.updated_at = datetime.now(timezone.utc)
        provider.updated_by = current_user.id

        self.session.add(provider)
        self.session.commit()
        self.session.refresh(provider)
        return provider

    def delete(
        self, provider_id: int, current_user: User
    ) -> ProviderDeleteResponse:
        provider = self.get(provider_id)
        if provider.status == ProviderStatus.INACTIVE:
            raise ConflictError(
                f"El proveedor con id '{provider_id}' ya fue eliminado."
            )

        now = datetime.now(timezone.utc)
        provider.deleted_at = now
        provider.deleted_by = current_user.id
        provider.status = ProviderStatus.INACTIVE

        self.session.add(provider)
        self.session.commit()

        return ProviderDeleteResponse(
            message=f"Proveedor '{provider.company}' eliminado correctamente.",
            deleted_at=now,
            deleted_by=current_user.id,
        )

    def create_contact(
        self, provider_id: int, data: ProviderContactCreate, current_user: User
    ) -> ProviderContact:
        provider = self.get(provider_id)
        if provider.status == ProviderStatus.INACTIVE:
            raise ConflictError(
                "No se pueden agregar contactos a un proveedor inactivo."
            )

        new_contact = ProviderContact(
            **data.model_dump(),
            provider_id=provider_id,
            created_by=current_user.id,
        )
        self.session.add(new_contact)
        self.session.commit()
        self.session.refresh(new_contact)
        return new_contact

    def update_contact(
        self,
        provider_id: int,
        contact_id: int,
        data: ProviderContactUpdate,
        current_user: User,
    ) -> ProviderContact:
        self.get(provider_id)

        contact = self.session.get(ProviderContact, contact_id)
        if not contact or contact.provider_id != provider_id:
            raise NotFoundError(
                f"El contacto con id '{contact_id}' no existe en este proveedor."
            )
        if contact.deleted_at is not None:
            raise ConflictError(
                f"El contacto con id '{contact_id}' está eliminado."
            )

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(contact, field, value)

        contact.updated_at = datetime.now(timezone.utc)
        contact.updated_by = current_user.id

        self.session.add(contact)
        self.session.commit()
        self.session.refresh(contact)
        return contact

    def delete_contact(
        self, provider_id: int, contact_id: int, current_user: User
    ) -> ProviderDeleteResponse:
        self.get(provider_id)

        contact = self.session.get(ProviderContact, contact_id)
        if not contact or contact.provider_id != provider_id:
            raise NotFoundError(
                f"El contacto con id '{contact_id}' no existe en este proveedor."
            )
        if contact.deleted_at is not None:
            raise ConflictError(
                f"El contacto con id '{contact_id}' ya fue eliminado."
            )

        now = datetime.now(timezone.utc)
        contact.deleted_at = now
        contact.deleted_by = current_user.id

        self.session.add(contact)
        self.session.commit()

        return ProviderDeleteResponse(
            message=f"Contacto '{contact.name}' eliminado correctamente.",
            deleted_at=now,
            deleted_by=current_user.id,
        )

    def bulk_import_providers(self, file, current_user: User) -> BulkImportResult:
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
                raise RowError(
                    f"El NIT '{row.get('nit')}' ya aparece en otra fila del archivo."
                )
            if email and email in seen_email:
                raise RowError(
                    f"El email '{row.get('email')}' ya aparece en otra fila del archivo."
                )

            if self.session.exec(
                select(Provider).where(Provider.nit_hash == blind_index(nit))
            ).first():
                raise RowError(
                    f"Ya existe un proveedor con el NIT '{row.get('nit')}'."
                )
            if email and self.session.exec(
                select(Provider).where(Provider.email == email)
            ).first():
                raise RowError(
                    f"Ya existe un proveedor con el email '{row.get('email')}'."
                )

            seen_nit.add(nit)
            if email:
                seen_email.add(email)

            self.session.add(
                Provider(
                    company=empresa,
                    nit=nit,
                    email=email,
                    created_by=current_user.id,
                )
            )
            return False

        return run_bulk(self.session, rows, process_row)

    def bulk_import_contacts(self, file, current_user: User) -> BulkImportResult:
        rows = parse_spreadsheet(file)
        providers = {
            name_key(p.company): p
            for p in self.session.exec(select(Provider)).all()
            if p.deleted_at is None and p.status == ProviderStatus.ACTIVE
        }

        def process_row(row):
            empresa = required_raw(row, "empresa_proveedor", "empresa_proveedor")
            provider = providers.get(name_key(empresa))
            if provider is None:
                raise RowError(
                    f"No existe el proveedor '{row.get('empresa_proveedor')}'."
                )

            nombre = required_raw(row, "nombre", "nombre")
            if len(nombre) > 150:
                raise RowError("El nombre del contacto supera los 150 caracteres.")

            email = str(row.get("email") or "").strip().lower()
            if email:
                _valid_email(email)

            telefono = row.get("telefono")
            if telefono is not None and len(str(telefono).strip()) > 20:
                raise RowError("El teléfono supera los 20 caracteres.")

            self.session.add(
                ProviderContact(
                    provider_id=provider.id,
                    name=nombre,
                    email=email or None,
                    phone=(
                        str(telefono).strip()
                        if telefono is not None and str(telefono).strip()
                        else None
                    ),
                    notes=optional_text(row, "notas"),
                    created_by=current_user.id,
                )
            )
            return False

        return run_bulk(self.session, rows, process_row)

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer, event
from sqlmodel import Field, Relationship, SQLModel

from src.core.crypto import EncryptedString, blind_index
from src.core.time import BOGOTA_TZ


class ProviderStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Provider(SQLModel, table=True):
    __tablename__ = "providers"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)

    company: str = Field(max_length=150)
    nit: str = Field(max_length=20, sa_type=EncryptedString(255))
    nit_hash: str = Field(default="", max_length=64, unique=True, index=True)
    email: str = Field(max_length=150, unique=True, index=True)
    status: ProviderStatus = Field(default=ProviderStatus.ACTIVE)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")

    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_provider_updated_by"),
            nullable=True,
        ),
    )

    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_provider_deleted_by"),
            nullable=True,
        ),
    )

    contacts: List["ProviderContact"] = Relationship(back_populates="provider")
    commercial_products: List["CommercialProduct"] = Relationship(  # noqa: F821
        back_populates="provider",
        sa_relationship_kwargs={"foreign_keys": "[CommercialProduct.provider_id]"},
    )


@event.listens_for(Provider, "before_insert")
@event.listens_for(Provider, "before_update")
def set_provider_nit_hash(mapper, connection, target) -> None:  # noqa: ANN001, ARG001
    """Mantiene el índice ciego sin depender de validadores de Pydantic."""
    if target.nit:
        target.nit_hash = blind_index(target.nit)


class ProviderContact(SQLModel, table=True):
    __tablename__ = "provider_contacts"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)

    provider_id: int = Field(foreign_key="providers.id")
    provider: "Provider" = Relationship(back_populates="contacts")

    name: str = Field(max_length=150)
    email: Optional[str] = Field(default=None, max_length=150)
    phone: Optional[str] = Field(default=None, sa_type=EncryptedString(255))
    notes: Optional[str] = Field(default=None, max_length=500)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")

    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey(
                "users.id", use_alter=True, name="fk_provider_contact_updated_by"
            ),
            nullable=True,
        ),
    )

    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey(
                "users.id", use_alter=True, name="fk_provider_contact_deleted_by"
            ),
            nullable=True,
        ),
    )

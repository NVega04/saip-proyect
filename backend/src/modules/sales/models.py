from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel

from src.core.time import BOGOTA_TZ


class SaleStatus(str, Enum):
    COMPLETED = "completada"
    ANNULLED = "anulada"


class ItemType(str, Enum):
    PRODUCT = "product"
    COMMERCIAL = "commercial"
    SUPPLY = "supply"


class MovementType(str, Enum):
    SALE = "sale"
    SALE_ANNULMENT = "sale_annulment"
    ENTRY = "entry"
    MANUAL = "manual"


class Sale(SQLModel, table=True):
    __tablename__ = "sales"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)

    user_id: int = Field(foreign_key="users.id")
    user: "User" = Relationship(  # noqa: F821
        sa_relationship_kwargs={"foreign_keys": "[Sale.user_id]"}
    )

    sale_date: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    status: SaleStatus = Field(default=SaleStatus.COMPLETED)
    notes: Optional[str] = Field(default=None, max_length=500)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_sale_updated_by"),
            nullable=True,
        ),
    )
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_sale_deleted_by"),
            nullable=True,
        ),
    )

    items: List["SaleItem"] = Relationship(back_populates="sale")


class SaleItem(SQLModel, table=True):
    __tablename__ = "sale_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)

    sale_id: int = Field(foreign_key="sales.id")
    sale: "Sale" = Relationship(back_populates="items")

    item_type: ItemType = Field(default=ItemType.PRODUCT)
    item_id: int
    item_name: str = Field(max_length=150)
    quantity: float = Field(default=0)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))

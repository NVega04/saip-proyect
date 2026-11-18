from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel

from src.core.time import BOGOTA_TZ


class ProductCategory(SQLModel, table=True):
    __tablename__ = "product_categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)
    name: str = Field(max_length=100, unique=True)
    description: Optional[str] = Field(default=None, max_length=255)
    status: str = Field(default="active")

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey(
                "users.id", use_alter=True, name="fk_product_category_updated_by"
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
                "users.id", use_alter=True, name="fk_product_category_deleted_by"
            ),
            nullable=True,
        ),
    )

    commercial_products: List["CommercialProduct"] = Relationship(
        back_populates="category"
    )


class CommercialProduct(SQLModel, table=True):
    __tablename__ = "commercial_products"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)
    name: str = Field(max_length=150)
    description: Optional[str] = Field(default=None, max_length=500)

    category_id: int = Field(foreign_key="product_categories.id")
    category: "ProductCategory" = Relationship(back_populates="commercial_products")

    unit_id: int = Field(foreign_key="units.id")
    unit: "Unit" = Relationship(  # noqa: F821
        sa_relationship_kwargs={"foreign_keys": "[CommercialProduct.unit_id]"}
    )

    provider_id: Optional[int] = Field(default=None, foreign_key="providers.id")
    provider: Optional["Provider"] = Relationship(  # noqa: F821
        sa_relationship_kwargs={"foreign_keys": "[CommercialProduct.provider_id]"}
    )

    purchase_price: float = Field(default=0)
    sale_price: float = Field(default=0)
    available_quantity: float = Field(default=0)
    min_stock: float = Field(default=0)
    max_stock: float = Field(default=0)
    status: str = Field(default="active")

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey(
                "users.id", use_alter=True, name="fk_commercial_product_updated_by"
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
                "users.id", use_alter=True, name="fk_commercial_product_deleted_by"
            ),
            nullable=True,
        ),
    )

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlmodel import Field, Relationship, SQLModel

from src.core.time import BOGOTA_TZ


class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)
    name: str = Field(max_length=150)
    description: Optional[str] = Field(default=None, max_length=500)
    unit_id: int = Field(foreign_key="units.id")
    available_quantity: float = Field(default=0)
    min_stock: float = Field(default=0)
    max_stock: float = Field(default=0)
    is_locked: bool = Field(default=False)
    status: str = Field(default="active")

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(default=None, foreign_key="users.id")

    unit: "Unit" = Relationship(back_populates="products")  # noqa: F821
    recipe: Optional["Recipe"] = Relationship(  # noqa: F821
        back_populates="product",
        sa_relationship_kwargs={"foreign_keys": "[Recipe.product_id]"},
    )

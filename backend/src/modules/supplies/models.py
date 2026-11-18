from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel

from src.core.time import BOGOTA_TZ


class SupplyCategory(SQLModel, table=True):
    __tablename__ = "supply_categories"

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
            ForeignKey("users.id", use_alter=True, name="fk_supply_category_updated_by"),
            nullable=True,
        ),
    )
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_supply_category_deleted_by"),
            nullable=True,
        ),
    )

    supplies: List["Supply"] = Relationship(back_populates="category")


class Supply(SQLModel, table=True):
    __tablename__ = "supplies"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)
    name: str = Field(max_length=150, unique=True)
    description: Optional[str] = Field(default=None, max_length=500)

    category_id: int = Field(foreign_key="supply_categories.id")
    category: "SupplyCategory" = Relationship(back_populates="supplies")

    unit_id: int = Field(foreign_key="units.id")
    unit: "Unit" = Relationship(back_populates="supplies")  # noqa: F821

    available_quantity: float = Field(default=0)
    min_stock: float = Field(default=0)
    max_stock: float = Field(default=0)
    supplier_id: Optional[int] = Field(default=None, foreign_key="users.id")
    expiration_date: Optional[datetime] = Field(default=None)
    status: str = Field(default="active")

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_supply_updated_by"),
            nullable=True,
        ),
    )
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_supply_deleted_by"),
            nullable=True,
        ),
    )

    recipe_ingredients: List["RecipeIngredient"] = Relationship(  # noqa: F821
        back_populates="supply"
    )

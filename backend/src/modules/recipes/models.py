from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel

from src.core.time import BOGOTA_TZ


class RecipeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Recipe(SQLModel, table=True):
    __tablename__ = "recipes"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)
    name: str = Field(max_length=150)
    description: Optional[str] = Field(default=None, max_length=500)

    product_id: Optional[int] = Field(default=None, foreign_key="products.id")
    product: Optional["Product"] = Relationship(  # noqa: F821
        back_populates="recipe"
    )

    yield_quantity: float = Field(default=1)
    yield_unit_id: int = Field(foreign_key="units.id")
    yield_unit: "Unit" = Relationship(  # noqa: F821
        sa_relationship_kwargs={"foreign_keys": "[Recipe.yield_unit_id]"}
    )

    status: RecipeStatus = Field(default=RecipeStatus.ACTIVE)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_recipe_updated_by"),
            nullable=True,
        ),
    )
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_recipe_deleted_by"),
            nullable=True,
        ),
    )

    ingredients: List["RecipeIngredient"] = Relationship(back_populates="recipe")
    production_orders: List["ProductionOrder"] = Relationship(  # noqa: F821
        back_populates="recipe"
    )


class RecipeIngredient(SQLModel, table=True):
    __tablename__ = "recipe_ingredients"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)

    recipe_id: int = Field(foreign_key="recipes.id")
    recipe: "Recipe" = Relationship(back_populates="ingredients")

    supply_id: int = Field(foreign_key="supplies.id")
    supply: "Supply" = Relationship(back_populates="recipe_ingredients")  # noqa: F821

    quantity: float = Field(default=0)
    unit_id: int = Field(foreign_key="units.id")
    unit: "Unit" = Relationship(  # noqa: F821
        sa_relationship_kwargs={"foreign_keys": "[RecipeIngredient.unit_id]"}
    )

    notes: Optional[str] = Field(default=None, max_length=255)

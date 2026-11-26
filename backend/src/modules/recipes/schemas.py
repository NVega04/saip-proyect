from datetime import datetime

from pydantic import BaseModel, field_validator

from src.core.schemas import UppercaseMixin
from src.modules.recipes.models import RecipeStatus
from src.modules.supplies.schemas import SupplyBasic
from src.modules.units.schemas import UnitBasic


class RecipeIngredientCreate(BaseModel):
    supply_id: int
    quantity: float
    unit_id: int
    notes: str | None = None


class RecipeIngredientResponse(BaseModel):
    id: int
    token: str
    supply_id: int
    supply: SupplyBasic
    quantity: float
    unit_id: int
    unit: UnitBasic
    notes: str | None

    class Config:
        from_attributes = True


class RecipeCreate(UppercaseMixin, BaseModel):
    name: str
    description: str | None = None
    product_id: int
    yield_quantity: float = 1
    yield_unit_id: int
    ingredients: list[RecipeIngredientCreate]


class RecipeUpdate(UppercaseMixin, BaseModel):
    name: str | None = None
    description: str | None = None
    product_id: int | None = None
    yield_quantity: float | None = None
    yield_unit_id: int | None = None
    status: RecipeStatus | None = None
    ingredients: list[RecipeIngredientCreate] | None = None


class RecipeResponse(BaseModel):
    id: int
    token: str
    name: str
    description: str | None
    product_id: int | None
    yield_quantity: float
    yield_unit_id: int
    yield_unit: UnitBasic
    status: RecipeStatus
    ingredients: list[RecipeIngredientResponse]
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None

    class Config:
        from_attributes = True

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v):
        if isinstance(v, str):
            return RecipeStatus(v.lower())
        return v


class DeleteResponseRecipe(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int

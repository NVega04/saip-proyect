from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from src.core.schemas import UppercaseMixin
from src.modules.recipes.models import RecipeStatus
from src.modules.supplies.schemas import SupplyBasic
from src.modules.units.schemas import UnitBasic


class RecipeIngredientCreate(BaseModel):
    supply_id: int
    quantity: float
    unit_id: int
    notes: Optional[str] = None


class RecipeIngredientResponse(BaseModel):
    id: int
    token: str
    supply_id: int
    supply: SupplyBasic
    quantity: float
    unit_id: int
    unit: UnitBasic
    notes: Optional[str]

    class Config:
        from_attributes = True


class RecipeCreate(UppercaseMixin, BaseModel):
    name: str
    description: Optional[str] = None
    product_id: int
    yield_quantity: float = 1
    yield_unit_id: int
    ingredients: list[RecipeIngredientCreate]


class RecipeUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    product_id: Optional[int] = None
    yield_quantity: Optional[float] = None
    yield_unit_id: Optional[int] = None
    status: Optional[RecipeStatus] = None
    ingredients: Optional[list[RecipeIngredientCreate]] = None


class RecipeResponse(BaseModel):
    id: int
    token: str
    name: str
    description: Optional[str]
    product_id: Optional[int]
    yield_quantity: float
    yield_unit_id: int
    yield_unit: UnitBasic
    status: RecipeStatus
    ingredients: list[RecipeIngredientResponse]
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]

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

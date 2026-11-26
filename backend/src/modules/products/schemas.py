from datetime import datetime

from pydantic import BaseModel, field_validator

from src.core.schemas import UppercaseMixin
from src.modules.products.models import ProductStatus
from src.modules.units.schemas import UnitBasic


class ProductCreate(UppercaseMixin, BaseModel):
    name: str
    description: str | None = None
    unit_id: int
    available_quantity: float = 0
    min_stock: float = 0
    max_stock: float = 0
    is_locked: bool = False


class ProductUpdate(UppercaseMixin, BaseModel):
    name: str | None = None
    description: str | None = None
    unit_id: int | None = None
    available_quantity: float | None = None
    min_stock: float | None = None
    max_stock: float | None = None
    is_locked: bool | None = None


class ProductResponse(BaseModel):
    id: int
    token: str
    name: str
    description: str | None
    unit_id: int
    unit: UnitBasic
    available_quantity: float
    min_stock: float
    max_stock: float
    is_locked: bool
    status: ProductStatus
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
            return ProductStatus(v.lower())
        return v

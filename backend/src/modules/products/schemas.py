from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from src.core.schemas import UppercaseMixin
from src.modules.products.models import ProductStatus
from src.modules.units.schemas import UnitBasic


class ProductCreate(UppercaseMixin, BaseModel):
    name: str
    description: Optional[str] = None
    unit_id: int
    available_quantity: float = 0
    min_stock: float = 0
    max_stock: float = 0
    is_locked: bool = False


class ProductUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unit_id: Optional[int] = None
    available_quantity: Optional[float] = None
    min_stock: Optional[float] = None
    max_stock: Optional[float] = None
    is_locked: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    token: str
    name: str
    description: Optional[str]
    unit_id: int
    unit: UnitBasic
    available_quantity: float
    min_stock: float
    max_stock: float
    is_locked: bool
    status: ProductStatus
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
            return ProductStatus(v.lower())
        return v

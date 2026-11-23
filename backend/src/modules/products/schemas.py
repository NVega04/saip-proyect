from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.core.schemas import UppercaseMixin
from src.modules.products.models import ProductStatus
from src.modules.units.schemas import UnitBasic


class ProductCreate(UppercaseMixin, BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, max_length=500)
    unit_id: int = Field(gt=0)
    available_quantity: float = Field(default=0, ge=0)
    min_stock: float = Field(default=0, ge=0)
    max_stock: float = Field(default=0, ge=0)
    is_locked: bool = False


class ProductUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, max_length=500)
    unit_id: Optional[int] = Field(default=None, gt=0)
    available_quantity: Optional[float] = Field(default=None, ge=0)
    min_stock: Optional[float] = Field(default=None, ge=0)
    max_stock: Optional[float] = Field(default=None, ge=0)
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

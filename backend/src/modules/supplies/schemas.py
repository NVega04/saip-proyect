from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.core.schemas import UppercaseMixin
from src.modules.units.schemas import UnitBasic


class SupplyBasic(BaseModel):
    id: int
    token: str
    name: str
    status: str

    class Config:
        from_attributes = True


class SupplyCategoryBasic(BaseModel):
    id: int
    token: str
    name: str

    class Config:
        from_attributes = True


class SupplyCategoryCreate(UppercaseMixin, BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, max_length=500)


class SupplyCategoryUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, max_length=500)


class SupplyCategoryResponse(BaseModel):
    id: int
    token: str
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
    supplies: List[SupplyBasic]

    class Config:
        from_attributes = True


class DeleteResponseSupplyCategory(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int


class SupplyCreate(UppercaseMixin, BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    category_id: int = Field(gt=0)
    unit_id: int = Field(gt=0)
    available_quantity: float = Field(default=0, ge=0)
    min_stock: float = Field(default=0, ge=0)
    max_stock: float = Field(default=0, ge=0)
    supplier_id: Optional[int] = Field(default=None, gt=0)
    expiration_date: Optional[datetime] = None


class SupplyUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    category_id: Optional[int] = Field(default=None, gt=0)
    unit_id: Optional[int] = Field(default=None, gt=0)
    available_quantity: Optional[float] = Field(default=None, ge=0)
    min_stock: Optional[float] = Field(default=None, ge=0)
    max_stock: Optional[float] = Field(default=None, ge=0)
    supplier_id: Optional[int] = Field(default=None, gt=0)
    expiration_date: Optional[datetime] = None


class SupplyResponse(BaseModel):
    id: int
    token: str
    name: str
    description: Optional[str]
    category_id: int
    category: SupplyCategoryBasic
    unit_id: int
    unit: UnitBasic
    available_quantity: float
    min_stock: float
    max_stock: float
    supplier_id: Optional[int]
    expiration_date: Optional[datetime]
    status: str
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]

    class Config:
        from_attributes = True


class DeleteResponseSupply(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int

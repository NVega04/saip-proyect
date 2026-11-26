from datetime import datetime
from typing import List

from pydantic import BaseModel

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
    name: str
    description: str | None = None


class SupplyCategoryUpdate(UppercaseMixin, BaseModel):
    name: str | None = None
    description: str | None = None


class SupplyCategoryResponse(BaseModel):
    id: int
    token: str
    name: str
    description: str | None
    status: str
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None
    supplies: List[SupplyBasic]

    class Config:
        from_attributes = True


class DeleteResponseSupplyCategory(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int


class SupplyCreate(UppercaseMixin, BaseModel):
    name: str
    description: str | None = None
    category_id: int
    unit_id: int
    available_quantity: float = 0
    min_stock: float = 0
    max_stock: float = 0
    supplier_id: int | None = None
    expiration_date: datetime | None = None


class SupplyUpdate(UppercaseMixin, BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    unit_id: int | None = None
    available_quantity: float | None = None
    min_stock: float | None = None
    max_stock: float | None = None
    supplier_id: int | None = None
    expiration_date: datetime | None = None


class SupplyResponse(BaseModel):
    id: int
    token: str
    name: str
    description: str | None
    category_id: int
    category: SupplyCategoryBasic
    unit_id: int
    unit: UnitBasic
    available_quantity: float
    min_stock: float
    max_stock: float
    supplier_id: int | None
    expiration_date: datetime | None
    status: str
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None

    class Config:
        from_attributes = True


class DeleteResponseSupply(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int

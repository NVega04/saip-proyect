from datetime import datetime
from typing import List

from pydantic import BaseModel

from src.core.schemas import UppercaseMixin
from src.modules.units.schemas import UnitBasic


class ProductCategoryBasic(BaseModel):
    id: int
    token: str
    name: str

    class Config:
        from_attributes = True


class CommercialProductBasic(BaseModel):
    id: int
    token: str
    name: str
    status: str

    class Config:
        from_attributes = True


class ProductCategoryCreate(UppercaseMixin, BaseModel):
    name: str
    description: str | None = None


class ProductCategoryUpdate(UppercaseMixin, BaseModel):
    name: str | None = None
    description: str | None = None


class ProductCategoryResponse(BaseModel):
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
    commercial_products: List[CommercialProductBasic]

    class Config:
        from_attributes = True


class DeleteResponseProductCategory(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int


class ProviderBasic(BaseModel):
    id: int
    token: str
    company: str

    class Config:
        from_attributes = True


class CommercialProductCreate(UppercaseMixin, BaseModel):
    name: str
    description: str | None = None
    category_id: int
    unit_id: int
    provider_id: int | None = None
    purchase_price: float = 0
    sale_price: float = 0
    available_quantity: float = 0
    min_stock: float = 0
    max_stock: float = 0


class CommercialProductUpdate(UppercaseMixin, BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    unit_id: int | None = None
    provider_id: int | None = None
    purchase_price: float | None = None
    sale_price: float | None = None
    available_quantity: float | None = None
    min_stock: float | None = None
    max_stock: float | None = None


class CommercialProductResponse(BaseModel):
    id: int
    token: str
    name: str
    description: str | None
    category_id: int
    category: ProductCategoryBasic
    unit_id: int
    unit: UnitBasic
    provider_id: int | None
    provider: ProviderBasic | None
    purchase_price: float
    sale_price: float
    available_quantity: float
    min_stock: float
    max_stock: float
    status: str
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None

    class Config:
        from_attributes = True


class DeleteResponseCommercialProduct(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int

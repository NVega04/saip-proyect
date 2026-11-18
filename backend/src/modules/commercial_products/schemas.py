from datetime import datetime
from typing import List, Optional

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
    description: Optional[str] = None


class ProductCategoryUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProductCategoryResponse(BaseModel):
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
    description: Optional[str] = None
    category_id: int
    unit_id: int
    provider_id: Optional[int] = None
    purchase_price: float = 0
    sale_price: float = 0
    available_quantity: float = 0
    min_stock: float = 0
    max_stock: float = 0


class CommercialProductUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    unit_id: Optional[int] = None
    provider_id: Optional[int] = None
    purchase_price: Optional[float] = None
    sale_price: Optional[float] = None
    available_quantity: Optional[float] = None
    min_stock: Optional[float] = None
    max_stock: Optional[float] = None


class CommercialProductResponse(BaseModel):
    id: int
    token: str
    name: str
    description: Optional[str]
    category_id: int
    category: ProductCategoryBasic
    unit_id: int
    unit: UnitBasic
    provider_id: Optional[int]
    provider: Optional[ProviderBasic]
    purchase_price: float
    sale_price: float
    available_quantity: float
    min_stock: float
    max_stock: float
    status: str
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]

    class Config:
        from_attributes = True


class DeleteResponseCommercialProduct(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int

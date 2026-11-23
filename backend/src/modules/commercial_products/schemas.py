from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

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
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


class ProductCategoryUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


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
    name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, max_length=500)
    category_id: int = Field(gt=0)
    unit_id: int = Field(gt=0)
    provider_id: Optional[int] = Field(default=None, gt=0)
    purchase_price: float = Field(default=0, ge=0)
    sale_price: float = Field(default=0, ge=0)
    available_quantity: float = Field(default=0, ge=0)
    min_stock: float = Field(default=0, ge=0)
    max_stock: float = Field(default=0, ge=0)


class CommercialProductUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, max_length=500)
    category_id: Optional[int] = Field(default=None, gt=0)
    unit_id: Optional[int] = Field(default=None, gt=0)
    provider_id: Optional[int] = Field(default=None, gt=0)
    purchase_price: Optional[float] = Field(default=None, ge=0)
    sale_price: Optional[float] = Field(default=None, ge=0)
    available_quantity: Optional[float] = Field(default=None, ge=0)
    min_stock: Optional[float] = Field(default=None, ge=0)
    max_stock: Optional[float] = Field(default=None, ge=0)


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

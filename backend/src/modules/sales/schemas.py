from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_validator

from src.modules.sales.models import ItemType, SaleStatus


class UserBasic(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str

    class Config:
        from_attributes = True


class SaleItemCreate(BaseModel):
    item_type: ItemType
    item_id: int
    quantity: float = Field(gt=0)


class SaleCreate(BaseModel):
    items: List[SaleItemCreate] = Field(min_length=1)
    notes: str | None = Field(default=None, max_length=500)


class SaleItemResponse(BaseModel):
    id: int
    token: str
    item_type: ItemType
    item_id: int
    item_name: str
    quantity: float

    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    id: int
    token: str
    user_id: int
    user: UserBasic
    sale_date: datetime
    status: SaleStatus
    notes: str | None
    items: List[SaleItemResponse]
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
            return SaleStatus(v.lower())
        return v


class SaleListResponse(BaseModel):
    id: int
    token: str
    user_id: int
    user: UserBasic
    sale_date: datetime
    status: SaleStatus
    notes: str | None
    item_count: int
    total_quantity: float
    created_at: datetime

    class Config:
        from_attributes = True

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v):
        if isinstance(v, str):
            return SaleStatus(v.lower())
        return v


class StockWarning(BaseModel):
    item_type: ItemType
    item_id: int
    item_name: str
    available_quantity: float
    min_stock: float


class SaleListPage(BaseModel):
    items: List[SaleListResponse]
    total: int
    page: int
    limit: int


class SaleCreateResponse(BaseModel):
    sale: SaleResponse
    warnings: List[StockWarning]


class SaleAnnulRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


class SaleAnnulResponse(BaseModel):
    message: str
    id: int
    status: SaleStatus
    changed_at: datetime
    changed_by: int

from datetime import datetime
from typing import List, Optional

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
    item_id: int = Field(gt=0)
    quantity: float = Field(gt=0)


class SaleCreate(BaseModel):
    items: List[SaleItemCreate] = Field(min_length=1)
    notes: Optional[str] = Field(default=None, max_length=500)


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
    notes: Optional[str]
    items: List[SaleItemResponse]
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
            return SaleStatus(v.lower())
        return v


class SaleListResponse(BaseModel):
    id: int
    token: str
    user_id: int
    user: UserBasic
    sale_date: datetime
    status: SaleStatus
    notes: Optional[str]
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

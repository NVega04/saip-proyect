from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.modules.production.models import ProductionOrderStatus
from src.modules.supplies.schemas import SupplyBasic
from src.modules.units.schemas import UnitBasic


class RecipeBasic(BaseModel):
    id: int
    name: str
    product_id: Optional[int] = None
    yield_quantity: float
    yield_unit: UnitBasic

    class Config:
        from_attributes = True


class ProductionOrderCreate(BaseModel):
    recipe_id: int = Field(gt=0)
    quantity_multiplier: float = Field(gt=0)
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=500)


class ProductionOrderCancelRequest(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=500)


class ProductionOrderResponse(BaseModel):
    id: int
    token: str
    recipe_id: int
    recipe: RecipeBasic
    quantity_multiplier: float
    total_yield: float
    status: ProductionOrderStatus
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    notes: Optional[str]
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
            return ProductionOrderStatus(v.lower())
        return v


class ProductionOrderStatusChangeResponse(BaseModel):
    message: str
    id: int
    status: ProductionOrderStatus
    changed_at: datetime
    changed_by: int


class ProductionSnapshotResponse(BaseModel):
    id: int
    supply_id: int
    supply: SupplyBasic
    quantity_used: float
    unit_id: int
    unit: UnitBasic
    stock_before: float
    stock_after: float


class ProductionCompleteResponse(BaseModel):
    message: str
    id: int
    status: ProductionOrderStatus
    total_yield: float
    completed_at: datetime
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    product_quantity_added: Optional[float] = None
    snapshots: list[ProductionSnapshotResponse]
    completed_by: int

    class Config:
        from_attributes = True

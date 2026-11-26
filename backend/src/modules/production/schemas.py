from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from src.modules.production.models import ProductionOrderStatus
from src.modules.supplies.schemas import SupplyBasic
from src.modules.units.schemas import UnitBasic


class RecipeBasic(BaseModel):
    id: int
    name: str
    product_id: int | None = None
    yield_quantity: float
    yield_unit: UnitBasic

    class Config:
        from_attributes = True


class ProductionOrderCreate(BaseModel):
    recipe_id: int
    quantity_multiplier: float = Field(gt=0)
    scheduled_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=500)


class ProductionOrderCancelRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class ProductionOrderResponse(BaseModel):
    id: int
    token: str
    recipe_id: int
    recipe: RecipeBasic
    quantity_multiplier: float
    total_yield: float
    status: ProductionOrderStatus
    scheduled_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    notes: str | None
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
    product_id: int | None = None
    product_name: str | None = None
    product_quantity_added: float | None = None
    snapshots: list[ProductionSnapshotResponse]
    completed_by: int

    class Config:
        from_attributes = True

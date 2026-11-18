from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel

from src.core.time import BOGOTA_TZ


class ProductionOrderStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProductionOrder(SQLModel, table=True):
    __tablename__ = "production_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)

    recipe_id: int = Field(foreign_key="recipes.id")
    recipe: "Recipe" = Relationship(back_populates="production_orders")  # noqa: F821

    quantity_multiplier: float = Field(default=1)
    total_yield: float = Field(default=0)

    status: ProductionOrderStatus = Field(default=ProductionOrderStatus.PENDING)

    scheduled_at: Optional[datetime] = Field(default=None)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    cancelled_at: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=500)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey(
                "users.id", use_alter=True, name="fk_production_order_updated_by"
            ),
            nullable=True,
        ),
    )
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey(
                "users.id", use_alter=True, name="fk_production_order_deleted_by"
            ),
            nullable=True,
        ),
    )

    snapshots: List["ProductionOrderSnapshot"] = Relationship(
        back_populates="production_order"
    )


class ProductionOrderSnapshot(SQLModel, table=True):
    __tablename__ = "production_order_snapshots"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)

    production_order_id: int = Field(foreign_key="production_orders.id")
    production_order: "ProductionOrder" = Relationship(back_populates="snapshots")

    supply_id: int = Field(foreign_key="supplies.id")
    supply: "Supply" = Relationship()  # noqa: F821

    quantity_used: float
    unit_id: int = Field(foreign_key="units.id")
    unit: "Unit" = Relationship(  # noqa: F821
        sa_relationship_kwargs={"foreign_keys": "[ProductionOrderSnapshot.unit_id]"}
    )

    stock_before: float
    stock_after: float

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlmodel import Field, Relationship, SQLModel

from src.core.time import BOGOTA_TZ
from src.modules.sales.models import ItemType, MovementType


class InventoryMovement(SQLModel, table=True):
    __tablename__ = "inventory_movements"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)

    item_type: ItemType = Field(default=ItemType.PRODUCT)
    item_id: int
    movement_type: MovementType = Field(default=MovementType.SALE)
    quantity: float = Field(default=0)
    stock_before: float = Field(default=0)
    stock_after: float = Field(default=0)

    reference_type: Optional[str] = Field(default=None, max_length=50)
    reference_id: Optional[int] = Field(default=None)

    user_id: int = Field(foreign_key="users.id")
    user: "User" = Relationship(  # noqa: F821
        sa_relationship_kwargs={"foreign_keys": "[InventoryMovement.user_id]"}
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))

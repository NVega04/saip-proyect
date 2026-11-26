from enum import Enum
from typing import List

from pydantic import BaseModel


class InventoryItemStatus(str, Enum):
    LOW = "bajo"
    NORMAL = "normal"
    OVER = "sobre"


class InventoryItem(BaseModel):
    id: int
    item_type: str
    name: str
    description: str | None = None
    category_name: str | None = None
    unit_abbreviation: str | None = None
    available_quantity: float
    min_stock: float
    max_stock: float
    stock_status: InventoryItemStatus
    status: str


class InventorySummary(BaseModel):
    total_items: int
    bajo_stock: int
    sobre_stock: int


class InventoryPage(BaseModel):
    items: List[InventoryItem]
    total: int
    page: int
    limit: int
    summary: InventorySummary

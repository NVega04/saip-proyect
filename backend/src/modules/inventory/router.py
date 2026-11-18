from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse

from src.bulk.parser import template_response
from src.core.dependencies import require_module
from src.modules.inventory.dependencies import get_inventory_service
from src.modules.inventory.schemas import InventoryPage
from src.modules.inventory.service import (
    BULK_MOVEMENT_EXAMPLES,
    BULK_MOVEMENT_HEADERS,
    InventoryService,
)
from src.modules.users.models import User

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get(
    "/summary", response_model=InventoryPage, status_code=status.HTTP_200_OK
)
def inventory_summary(
    item_type: Optional[Literal["supply", "product", "commercial"]] = Query(
        default=None
    ),
    stock_status: Optional[Literal["bajo", "normal", "sobre"]] = Query(
        default=None
    ),
    category_id: Optional[int] = Query(default=None),
    search: Optional[str] = Query(default=None, max_length=150),
    status_filter: Optional[Literal["active", "inactive"]] = Query(
        default=None, alias="status"
    ),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(require_module("inventory")),
):
    return service.summary(
        item_type,
        stock_status,
        category_id,
        search,
        status_filter,
        page,
        limit,
    )


@router.get("/report", response_class=StreamingResponse)
def inventory_report(
    item_type: Optional[Literal["supply", "product", "commercial"]] = Query(
        default=None
    ),
    stock_status: Optional[Literal["bajo", "normal", "sobre"]] = Query(
        default=None
    ),
    category_id: Optional[int] = Query(default=None),
    search: Optional[str] = Query(default=None, max_length=150),
    status_filter: Optional[Literal["active", "inactive"]] = Query(
        default=None, alias="status"
    ),
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(require_module("inventory")),
):
    return service.report(
        item_type, stock_status, category_id, search, status_filter
    )


@router.get(
    "/bulk/template",
    status_code=status.HTTP_200_OK,
    summary="Descargar plantilla de movimientos de stock",
)
def bulk_movements_template():
    return template_response(
        "plantilla_movimientos_inventario.xlsx",
        BULK_MOVEMENT_HEADERS,
        BULK_MOVEMENT_EXAMPLES,
    )

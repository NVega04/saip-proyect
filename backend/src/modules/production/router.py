from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from src.bulk.parser import template_response
from src.core.dependencies import get_current_user
from src.core.schemas import BulkImportResult
from src.modules.production.dependencies import get_production_service
from src.modules.production.models import ProductionOrderStatus
from src.modules.production.schemas import (
    ProductionCompleteResponse,
    ProductionOrderCancelRequest,
    ProductionOrderCreate,
    ProductionOrderResponse,
    ProductionOrderStatusChangeResponse,
)
from src.modules.production.service import (
    BULK_ORDER_EXAMPLES,
    BULK_ORDER_HEADERS,
    ProductionService,
)
from src.modules.users.models import User

router = APIRouter(prefix="/production/orders", tags=["Production"])


@router.post(
    "/",
    response_model=ProductionOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    data: ProductionOrderCreate,
    service: ProductionService = Depends(get_production_service),
    current_user: User = Depends(get_current_user),
):
    return service.create(data, current_user)


@router.get(
    "/",
    response_model=list[ProductionOrderResponse],
    status_code=status.HTTP_200_OK,
)
def get_all(
    status_filter: Optional[ProductionOrderStatus] = Query(
        default=None, alias="status"
    ),
    service: ProductionService = Depends(get_production_service),
    current_user: User = Depends(get_current_user),
):
    return service.list(status_filter)


@router.get(
    "/export",
    summary="Exportar órdenes de producción a Excel",
)
def export_orders(
    status_filter: Optional[ProductionOrderStatus] = Query(
        default=None, alias="status"
    ),
    service: ProductionService = Depends(get_production_service),
    current_user: User = Depends(get_current_user),
):
    return service.export_orders(status_filter)


@router.get(
    "/{order_id}",
    response_model=ProductionOrderResponse,
    status_code=status.HTTP_200_OK,
)
def get_one(
    order_id: int,
    service: ProductionService = Depends(get_production_service),
    current_user: User = Depends(get_current_user),
):
    return service.get(order_id)


@router.patch(
    "/{order_id}/start",
    response_model=ProductionOrderStatusChangeResponse,
    status_code=status.HTTP_200_OK,
)
def start(
    order_id: int,
    service: ProductionService = Depends(get_production_service),
    current_user: User = Depends(get_current_user),
):
    return service.start(order_id, current_user)


@router.patch(
    "/{order_id}/cancel",
    response_model=ProductionOrderStatusChangeResponse,
    status_code=status.HTTP_200_OK,
)
def cancel(
    order_id: int,
    data: ProductionOrderCancelRequest,
    service: ProductionService = Depends(get_production_service),
    current_user: User = Depends(get_current_user),
):
    return service.cancel(order_id, data, current_user)


@router.post(
    "/{order_id}/complete",
    response_model=ProductionCompleteResponse,
    status_code=status.HTTP_200_OK,
)
def complete(
    order_id: int,
    service: ProductionService = Depends(get_production_service),
    current_user: User = Depends(get_current_user),
):
    return service.complete(order_id, current_user)


@router.post(
    "/bulk/import",
    response_model=BulkImportResult,
    status_code=status.HTTP_200_OK,
    summary="Cargar órdenes de producción por archivo Excel/CSV",
)
def bulk_import_orders(
    file: UploadFile = File(...),
    service: ProductionService = Depends(get_production_service),
    current_user: User = Depends(get_current_user),
):
    return service.bulk_import(file, current_user)


@router.get(
    "/bulk/template",
    status_code=status.HTTP_200_OK,
    summary="Descargar plantilla de órdenes de producción",
)
def bulk_orders_template():
    return template_response(
        "plantilla_ordenes_produccion.xlsx",
        BULK_ORDER_HEADERS,
        BULK_ORDER_EXAMPLES,
    )

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from src.core.dependencies import get_current_user, require_module
from src.modules.sales.dependencies import get_sales_service
from src.modules.sales.models import ItemType, SaleStatus
from src.modules.sales.schemas import (
    SaleAnnulRequest,
    SaleAnnulResponse,
    SaleCreate,
    SaleCreateResponse,
    SaleListPage,
    SaleResponse,
)
from src.modules.sales.service import SalesService
from src.modules.users.models import User

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post(
    "/", response_model=SaleCreateResponse, status_code=status.HTTP_201_CREATED
)
def create_sale(
    data: SaleCreate,
    service: SalesService = Depends(get_sales_service),
    current_user: User = Depends(get_current_user),
):
    return service.create(data, current_user)


@router.get("/", response_model=SaleListPage, status_code=status.HTTP_200_OK)
def get_sales(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    status_filter: Optional[SaleStatus] = Query(default=None, alias="status"),
    item_type: Optional[ItemType] = Query(default=None),
    item_id: Optional[int] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    service: SalesService = Depends(get_sales_service),
    current_user: User = Depends(get_current_user),
):
    return service.list(
        date_from,
        date_to,
        status_filter,
        item_type,
        item_id,
        page,
        limit,
    )


@router.get(
    "/export",
    summary="Exportar ventas a Excel (con los filtros de la vista)",
)
def export_sales(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    status_filter: Optional[SaleStatus] = Query(default=None, alias="status"),
    service: SalesService = Depends(get_sales_service),
    current_user: User = Depends(get_current_user),
):
    return service.export(date_from, date_to, status_filter)


@router.get(
    "/{sale_id}", response_model=SaleResponse, status_code=status.HTTP_200_OK
)
def get_sale(
    sale_id: int,
    service: SalesService = Depends(get_sales_service),
    current_user: User = Depends(get_current_user),
):
    return service.get(sale_id)


@router.patch(
    "/{sale_id}/annul",
    response_model=SaleAnnulResponse,
    status_code=status.HTTP_200_OK,
)
def annul_sale(
    sale_id: int,
    data: SaleAnnulRequest,
    service: SalesService = Depends(get_sales_service),
    current_user: User = Depends(require_module("sales")),
):
    return service.annul(sale_id, current_user, data.reason)

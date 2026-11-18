from typing import Literal

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from src.bulk.parser import template_response
from src.core.dependencies import get_current_user
from src.core.schemas import BulkImportResult
from src.modules.commercial_products.dependencies import (
    get_commercial_products_service,
)
from src.modules.commercial_products.schemas import (
    CommercialProductCreate,
    CommercialProductResponse,
    CommercialProductUpdate,
    DeleteResponseCommercialProduct,
)
from src.modules.commercial_products.service import (
    BULK_COMMERCIAL_EXAMPLES,
    BULK_COMMERCIAL_HEADERS,
    CommercialProductsService,
)
from src.modules.users.models import User

router = APIRouter(prefix="/commercial-products", tags=["CommercialProducts"])


@router.get(
    "/",
    response_model=list[CommercialProductResponse],
    status_code=status.HTTP_200_OK,
)
def get_all(
    service: CommercialProductsService = Depends(get_commercial_products_service),
    current_user: User = Depends(get_current_user),
):
    return service.list()


@router.get(
    "/{product_id}",
    response_model=CommercialProductResponse,
    status_code=status.HTTP_200_OK,
)
def get_one(
    product_id: int,
    service: CommercialProductsService = Depends(get_commercial_products_service),
    current_user: User = Depends(get_current_user),
):
    return service.get(product_id)


@router.post(
    "/",
    response_model=CommercialProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    data: CommercialProductCreate,
    service: CommercialProductsService = Depends(get_commercial_products_service),
    current_user: User = Depends(get_current_user),
):
    return service.create(data, current_user)


@router.patch(
    "/{product_id}",
    response_model=CommercialProductResponse,
    status_code=status.HTTP_200_OK,
)
def update(
    product_id: int,
    data: CommercialProductUpdate,
    service: CommercialProductsService = Depends(get_commercial_products_service),
    current_user: User = Depends(get_current_user),
):
    return service.update(product_id, data, current_user)


@router.delete(
    "/{product_id}",
    response_model=DeleteResponseCommercialProduct,
    status_code=status.HTTP_200_OK,
)
def delete(
    product_id: int,
    service: CommercialProductsService = Depends(get_commercial_products_service),
    current_user: User = Depends(get_current_user),
):
    return service.delete(product_id, current_user)


@router.post(
    "/bulk/import",
    response_model=BulkImportResult,
    status_code=status.HTTP_200_OK,
    summary="Cargar productos comerciales por archivo Excel/CSV (create o upsert)",
)
def bulk_import_commercial(
    mode: Literal["create", "upsert"] = Query(default="create"),
    file: UploadFile = File(...),
    service: CommercialProductsService = Depends(get_commercial_products_service),
    current_user: User = Depends(get_current_user),
):
    return service.bulk_import(mode, file, current_user)


@router.get(
    "/bulk/template",
    status_code=status.HTTP_200_OK,
    summary="Descargar plantilla de productos comerciales",
)
def bulk_commercial_template():
    return template_response(
        "plantilla_productos_comerciales.xlsx",
        BULK_COMMERCIAL_HEADERS,
        BULK_COMMERCIAL_EXAMPLES,
    )

from typing import Literal

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from src.bulk.parser import template_response
from src.core.dependencies import get_current_user
from src.core.pagination import Pagination
from src.core.schemas import BulkImportResult
from src.modules.products.dependencies import get_products_service
from src.modules.products.schemas import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from src.modules.products.service import (
    BULK_PRODUCT_EXAMPLES,
    BULK_PRODUCT_HEADERS,
    ProductsService,
)
from src.modules.users.models import User

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "/", response_model=list[ProductResponse], status_code=status.HTTP_200_OK
)
def get_products(
    pagination: Pagination,
    service: ProductsService = Depends(get_products_service),
):
    return service.list(pagination.skip, pagination.limit)


@router.get(
    "/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK
)
def get_product(
    product_id: int,
    service: ProductsService = Depends(get_products_service),
):
    return service.get(product_id)


@router.post(
    "/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED
)
def create_product(
    product_data: ProductCreate,
    service: ProductsService = Depends(get_products_service),
    current_user: User = Depends(get_current_user),
):
    return service.create(product_data, current_user)


@router.patch(
    "/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK
)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    service: ProductsService = Depends(get_products_service),
    current_user: User = Depends(get_current_user),
):
    return service.update(product_id, product_data, current_user)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    service: ProductsService = Depends(get_products_service),
    current_user: User = Depends(get_current_user),
):
    service.delete(product_id, current_user)
    return None


@router.patch(
    "/{product_id}/lock",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
)
def toggle_product_lock(
    product_id: int,
    service: ProductsService = Depends(get_products_service),
    current_user: User = Depends(get_current_user),
):
    return service.toggle_lock(product_id, current_user)


@router.post(
    "/bulk/import",
    response_model=BulkImportResult,
    status_code=status.HTTP_200_OK,
    summary="Cargar productos por archivo Excel/CSV (create o upsert)",
)
def bulk_import_products(
    mode: Literal["create", "upsert"] = Query(default="create"),
    file: UploadFile = File(...),
    service: ProductsService = Depends(get_products_service),
    current_user: User = Depends(get_current_user),
):
    return service.bulk_import(mode, file, current_user)


@router.get(
    "/bulk/template",
    status_code=status.HTTP_200_OK,
    summary="Descargar plantilla de productos",
)
def bulk_products_template():
    return template_response(
        "plantilla_productos.xlsx", BULK_PRODUCT_HEADERS, BULK_PRODUCT_EXAMPLES
    )

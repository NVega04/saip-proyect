from typing import Literal, Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from src.bulk.parser import template_response
from src.core.dependencies import get_current_user
from src.core.openapi import CONFLICT, NOT_FOUND
from src.core.pagination import Page, PaginationParams
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
    response_model=Page[CommercialProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar productos comerciales con paginación",
)
def get_all(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(
        default=None, max_length=100, description="Busca por nombre o descripción"
    ),
    service: CommercialProductsService = Depends(get_commercial_products_service),
    current_user: User = Depends(get_current_user),
):
    """Lista productos comerciales con paginación y búsqueda.

    Envelope ``{items, total, page, limit}``; ``page`` >= 1, ``limit`` 1..100
    (defecto 20). ``search`` filtra por nombre o descripción con ``LIKE`` y
    escapa ``%`` y ``_``.
    """
    return service.list(pagination, search)


@router.get(
    "/{product_id}",
    response_model=CommercialProductResponse,
    status_code=status.HTTP_200_OK,
    responses={404: NOT_FOUND},
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
    responses={404: NOT_FOUND, 409: CONFLICT},
)
def create(
    data: CommercialProductCreate,
    service: CommercialProductsService = Depends(get_commercial_products_service),
    current_user: User = Depends(get_current_user),
):
    """Crea un producto comercial a partir de un producto terminado.

    El producto de origen, la categoría y la unidad deben existir (404) y no
    puede existir otro producto comercial con el mismo nombre (409).
    """
    return service.create(data, current_user)


@router.patch(
    "/{product_id}",
    response_model=CommercialProductResponse,
    status_code=status.HTTP_200_OK,
    responses={404: NOT_FOUND, 409: CONFLICT},
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
    responses={404: NOT_FOUND},
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
def bulk_commercial_template(
    current_user: User = Depends(get_current_user),
):
    return template_response(
        "plantilla_productos_comerciales.xlsx",
        BULK_COMMERCIAL_HEADERS,
        BULK_COMMERCIAL_EXAMPLES,
    )

from typing import Literal, Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from src.bulk.parser import template_response
from src.core.dependencies import get_current_user
from src.core.openapi import CONFLICT, FORBIDDEN, NOT_FOUND
from src.core.pagination import Page, PaginationParams
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
    "/", response_model=Page[ProductResponse], status_code=status.HTTP_200_OK
)
def get_products(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(
        default=None, max_length=100, description="Busca por nombre o descripción"
    ),
    service: ProductsService = Depends(get_products_service),
    current_user: User = Depends(get_current_user),
):
    """Lista productos con paginación y búsqueda.

    Devuelve el envelope ``{items, total, page, limit}``. ``page`` empieza en 1
    y ``limit`` admite de 1 a 100 (defecto 20). ``search`` filtra por nombre o
    descripción con ``LIKE`` y escapa los comodines ``%`` y ``_``.
    """
    return service.list(pagination, search)


@router.get(
    "/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK
)
def get_product(
    product_id: int,
    service: ProductsService = Depends(get_products_service),
    current_user: User = Depends(get_current_user),
):
    """Devuelve un producto por id, o 404 si no existe o está eliminado."""
    return service.get(product_id)


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    responses={404: NOT_FOUND, 409: CONFLICT},
)
def create_product(
    product_data: ProductCreate,
    service: ProductsService = Depends(get_products_service),
    current_user: User = Depends(get_current_user),
):
    """Crea un producto.

    Reglas de negocio: la unidad debe existir (404) y el nombre no puede
    repetirse entre productos activos (409). La acción se registra en la auditoría.
    """
    return service.create(product_data, current_user)


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    responses={403: FORBIDDEN, 404: NOT_FOUND, 409: CONFLICT},
)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    service: ProductsService = Depends(get_products_service),
    current_user: User = Depends(get_current_user),
):
    """Actualiza un producto.

    Un producto bloqueado no se puede modificar (403); tampoco se puede
    renombrar a un nombre ya existente (409) ni asignar una unidad inexistente
    (404).
    """
    return service.update(product_id, product_data, current_user)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={403: FORBIDDEN, 404: NOT_FOUND},
)
def delete_product(
    product_id: int,
    service: ProductsService = Depends(get_products_service),
    current_user: User = Depends(get_current_user),
):
    """Elimina un producto (soft delete).

    La fila se marca con ``deleted_at``/``deleted_by``; no se borra físicamente.
    Un producto bloqueado no puede eliminarse (403) y un id inexistente
    devuelve 404.
    """
    service.delete(product_id, current_user)
    return None


@router.patch(
    "/{product_id}/lock",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    responses={404: NOT_FOUND},
)
def toggle_product_lock(
    product_id: int,
    service: ProductsService = Depends(get_products_service),
    current_user: User = Depends(get_current_user),
):
    """Alterna el bloqueo de un producto.

    Mientras ``is_locked`` es ``true``, el producto no puede modificarse ni
    eliminarse, pero sigue apareciendo en listados y se puede desbloquear con
    esta misma operación.
    """
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
    """Importa productos desde Excel/CSV.

    ``mode=create`` rechaza los nombres ya existentes; ``mode=upsert``
    actualiza descripción y niveles de stock de los productos existentes
    (nunca los bloqueados). Los errores de fila se devuelven dentro de
    ``BulkImportResult``, no como código HTTP; el resultado incluye cuántas
    filas se crearon, actualizaron y fallaron.
    """
    return service.bulk_import(mode, file, current_user)


@router.get(
    "/bulk/template",
    status_code=status.HTTP_200_OK,
    summary="Descargar plantilla de productos",
)
def bulk_products_template(
    current_user: User = Depends(get_current_user),
):
    return template_response(
        "plantilla_productos.xlsx", BULK_PRODUCT_HEADERS, BULK_PRODUCT_EXAMPLES
    )

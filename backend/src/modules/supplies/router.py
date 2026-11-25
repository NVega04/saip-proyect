from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from src.bulk.parser import template_response
from src.core.dependencies import get_current_user
from src.core.openapi import CONFLICT, NOT_FOUND
from src.core.pagination import Page, PaginationParams
from src.core.schemas import BulkImportResult
from src.modules.supplies.dependencies import get_supplies_service
from src.modules.supplies.schemas import (
    DeleteResponseSupply,
    SupplyCreate,
    SupplyResponse,
    SupplyUpdate,
)
from src.modules.supplies.service import (
    BULK_SUPPLY_EXAMPLES,
    BULK_SUPPLY_HEADERS,
    SuppliesService,
)
from src.modules.users.models import User

router = APIRouter(prefix="/supplies", tags=["Supplies"])


@router.post(
    "/",
    response_model=SupplyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo insumo",
    responses={404: NOT_FOUND, 409: CONFLICT},
)
def create_supply(
    data: SupplyCreate,
    service: SuppliesService = Depends(get_supplies_service),
    current_user: User = Depends(get_current_user),
):
    """Crea un insumo.

    La categoría y la unidad deben existir (404) y el nombre no puede
    repetirse entre insumos activos (409).
    """
    return service.create(data, current_user)


@router.get(
    "/",
    response_model=Page[SupplyResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar insumos activos con paginación",
)
def get_all_supplies(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(
        default=None, max_length=100, description="Busca por nombre o descripción"
    ),
    service: SuppliesService = Depends(get_supplies_service),
    current_user: User = Depends(get_current_user),
):
    """Lista insumos con paginación y búsqueda.

    Envelope ``{items, total, page, limit}``; ``page`` >= 1, ``limit`` 1..100
    (defecto 20). ``search`` filtra por nombre o descripción con ``LIKE`` y
    escapa ``%`` y ``_`` para que no actúen como comodines.
    """
    return service.list(pagination, search)


@router.get(
    "/{supply_id}",
    response_model=SupplyResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener insumo por ID",
    responses={404: NOT_FOUND},
)
def get_supply(
    supply_id: int,
    service: SuppliesService = Depends(get_supplies_service),
    current_user: User = Depends(get_current_user),
):
    return service.get(supply_id)


@router.put(
    "/{supply_id}",
    response_model=SupplyResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar insumo",
    responses={404: NOT_FOUND, 409: CONFLICT},
)
def update_supply(
    supply_id: int,
    data: SupplyUpdate,
    service: SuppliesService = Depends(get_supplies_service),
    current_user: User = Depends(get_current_user),
):
    return service.update(supply_id, data, current_user)


@router.delete(
    "/{supply_id}",
    response_model=DeleteResponseSupply,
    status_code=status.HTTP_200_OK,
    summary="Eliminar insumo (soft delete)",
    responses={404: NOT_FOUND, 409: CONFLICT},
)
def delete_supply(
    supply_id: int,
    service: SuppliesService = Depends(get_supplies_service),
    current_user: User = Depends(get_current_user),
):
    return service.delete(supply_id, current_user)


@router.post(
    "/bulk/import",
    response_model=BulkImportResult,
    status_code=status.HTTP_200_OK,
    summary="Cargar insumos por archivo Excel/CSV",
)
def bulk_import_supplies(
    file: UploadFile = File(...),
    service: SuppliesService = Depends(get_supplies_service),
    current_user: User = Depends(get_current_user),
):
    return service.bulk_import(file, current_user)


@router.get(
    "/bulk/template",
    status_code=status.HTTP_200_OK,
    summary="Descargar plantilla de insumos",
)
def bulk_supplies_template(
    current_user: User = Depends(get_current_user),
):
    return template_response(
        "plantilla_insumos.xlsx", BULK_SUPPLY_HEADERS, BULK_SUPPLY_EXAMPLES
    )

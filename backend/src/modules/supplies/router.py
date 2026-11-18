from fastapi import APIRouter, Depends, File, UploadFile, status

from src.bulk.parser import template_response
from src.core.dependencies import get_current_user
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
)
def create_supply(
    data: SupplyCreate,
    service: SuppliesService = Depends(get_supplies_service),
    current_user: User = Depends(get_current_user),
):
    return service.create(data, current_user)


@router.get(
    "/",
    response_model=list[SupplyResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los insumos activos",
)
def get_all_supplies(
    service: SuppliesService = Depends(get_supplies_service),
    current_user: User = Depends(get_current_user),
):
    return service.list()


@router.get(
    "/{supply_id}",
    response_model=SupplyResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener insumo por ID",
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
def bulk_supplies_template():
    return template_response(
        "plantilla_insumos.xlsx", BULK_SUPPLY_HEADERS, BULK_SUPPLY_EXAMPLES
    )

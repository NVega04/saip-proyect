from fastapi import APIRouter, Depends, status

from src.core.dependencies import get_current_user
from src.core.pagination import Pagination
from src.modules.supplies.categories_service import SupplyCategoriesService
from src.modules.supplies.dependencies import get_supply_categories_service
from src.modules.supplies.schemas import (
    DeleteResponseSupplyCategory,
    SupplyCategoryCreate,
    SupplyCategoryResponse,
    SupplyCategoryUpdate,
)
from src.modules.users.models import User

router = APIRouter(prefix="/supply-categories", tags=["SupplyCategories"])


@router.post(
    "/",
    response_model=SupplyCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva categoría de insumo",
)
def create_supply_category(
    data: SupplyCategoryCreate,
    service: SupplyCategoriesService = Depends(get_supply_categories_service),
    current_user: User = Depends(get_current_user),
):
    return service.create(data, current_user)


@router.get(
    "/",
    response_model=list[SupplyCategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todas las categorías de insumos",
)
def get_all_supply_categories(
    pagination: Pagination,
    service: SupplyCategoriesService = Depends(get_supply_categories_service),
    current_user: User = Depends(get_current_user),
):
    return service.list(pagination.skip, pagination.limit)


@router.get(
    "/{category_id}",
    response_model=SupplyCategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener categoría de insumo por ID",
)
def get_supply_category(
    category_id: int,
    service: SupplyCategoriesService = Depends(get_supply_categories_service),
    current_user: User = Depends(get_current_user),
):
    return service.get(category_id)


@router.put(
    "/{category_id}",
    response_model=SupplyCategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar categoría de insumo",
)
def update_supply_category(
    category_id: int,
    data: SupplyCategoryUpdate,
    service: SupplyCategoriesService = Depends(get_supply_categories_service),
    current_user: User = Depends(get_current_user),
):
    return service.update(category_id, data, current_user)


@router.delete(
    "/{category_id}",
    response_model=DeleteResponseSupplyCategory,
    status_code=status.HTTP_200_OK,
    summary="Eliminar categoría de insumo (soft delete)",
)
def delete_supply_category(
    category_id: int,
    service: SupplyCategoriesService = Depends(get_supply_categories_service),
    current_user: User = Depends(get_current_user),
):
    return service.delete(category_id, current_user)

from fastapi import APIRouter, Depends, status

from src.core.dependencies import get_current_user
from src.core.pagination import Pagination
from src.modules.commercial_products.categories_service import (
    ProductCategoriesService,
)
from src.modules.commercial_products.dependencies import (
    get_product_categories_service,
)
from src.modules.commercial_products.schemas import (
    DeleteResponseProductCategory,
    ProductCategoryCreate,
    ProductCategoryResponse,
    ProductCategoryUpdate,
)
from src.modules.users.models import User

router = APIRouter(prefix="/product-categories", tags=["ProductCategories"])


@router.get(
    "/",
    response_model=list[ProductCategoryResponse],
    status_code=status.HTTP_200_OK,
)
def get_all(
    pagination: Pagination,
    service: ProductCategoriesService = Depends(get_product_categories_service),
    current_user: User = Depends(get_current_user),
):
    return service.list(pagination.skip, pagination.limit)


@router.get(
    "/{category_id}",
    response_model=ProductCategoryResponse,
    status_code=status.HTTP_200_OK,
)
def get_one(
    category_id: int,
    service: ProductCategoriesService = Depends(get_product_categories_service),
    current_user: User = Depends(get_current_user),
):
    return service.get(category_id)


@router.post(
    "/",
    response_model=ProductCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    data: ProductCategoryCreate,
    service: ProductCategoriesService = Depends(get_product_categories_service),
    current_user: User = Depends(get_current_user),
):
    return service.create(data, current_user)


@router.put(
    "/{category_id}",
    response_model=ProductCategoryResponse,
    status_code=status.HTTP_200_OK,
)
def update(
    category_id: int,
    data: ProductCategoryUpdate,
    service: ProductCategoriesService = Depends(get_product_categories_service),
    current_user: User = Depends(get_current_user),
):
    return service.update(category_id, data, current_user)


@router.delete(
    "/{category_id}",
    response_model=DeleteResponseProductCategory,
    status_code=status.HTTP_200_OK,
)
def delete(
    category_id: int,
    service: ProductCategoriesService = Depends(get_product_categories_service),
    current_user: User = Depends(get_current_user),
):
    return service.delete(category_id, current_user)

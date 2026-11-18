from fastapi import APIRouter, Depends, status

from src.core.dependencies import get_current_user
from src.modules.recipes.dependencies import get_recipes_service
from src.modules.recipes.schemas import (
    DeleteResponseRecipe,
    RecipeCreate,
    RecipeResponse,
    RecipeUpdate,
)
from src.modules.recipes.service import RecipesService
from src.modules.users.models import User

router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.get(
    "/", response_model=list[RecipeResponse], status_code=status.HTTP_200_OK
)
def get_all(
    service: RecipesService = Depends(get_recipes_service),
    current_user: User = Depends(get_current_user),
):
    return service.list()


@router.get(
    "/{recipe_id}", response_model=RecipeResponse, status_code=status.HTTP_200_OK
)
def get_one(
    recipe_id: int,
    service: RecipesService = Depends(get_recipes_service),
    current_user: User = Depends(get_current_user),
):
    return service.get(recipe_id)


@router.post(
    "/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED
)
def create(
    data: RecipeCreate,
    service: RecipesService = Depends(get_recipes_service),
    current_user: User = Depends(get_current_user),
):
    return service.create(data, current_user)


@router.patch(
    "/{recipe_id}", response_model=RecipeResponse, status_code=status.HTTP_200_OK
)
def update(
    recipe_id: int,
    data: RecipeUpdate,
    service: RecipesService = Depends(get_recipes_service),
    current_user: User = Depends(get_current_user),
):
    return service.update(recipe_id, data, current_user)


@router.delete(
    "/{recipe_id}",
    response_model=DeleteResponseRecipe,
    status_code=status.HTTP_200_OK,
)
def delete(
    recipe_id: int,
    service: RecipesService = Depends(get_recipes_service),
    current_user: User = Depends(get_current_user),
):
    return service.delete(recipe_id, current_user)

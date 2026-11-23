from fastapi import APIRouter, Depends, Header, Request, status

from src.core.dependencies import get_current_user
from src.core.pagination import Pagination
from src.core.rate_limit import limiter
from src.modules.users.dependencies import get_users_service
from src.modules.users.schemas import (
    DeleteResponseUser,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserUpdateResponse,
)
from src.modules.users.service import UsersService
from src.modules.users.models import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo usuario",
)
@limiter.limit("10/minute")
def create_new_user(
    request: Request,
    user_data: UserCreate,
    service: UsersService = Depends(get_users_service),
):
    return service.create(user_data)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario autenticado",
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.delete(
    "/me",
    response_model=DeleteResponseUser,
    status_code=status.HTTP_200_OK,
    summary="Eliminar cuenta propia con confirmación de contraseña",
)
def delete_own_account(
    service: UsersService = Depends(get_users_service),
    current_user: User = Depends(get_current_user),
    x_confirm_password: str = Header(..., alias="X-Confirm-Password"),
):
    return service.delete_own_account(x_confirm_password, current_user)


@router.delete(
    "/{user_id}",
    response_model=DeleteResponseUser,
    status_code=status.HTTP_200_OK,
    summary="Eliminar usuario (soft delete)",
)
def delete_user(
    user_id: int,
    service: UsersService = Depends(get_users_service),
    current_user: User = Depends(get_current_user),
):
    return service.delete_user(user_id, current_user)


@router.put(
    "/{user_id}",
    response_model=UserUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario",
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: UsersService = Depends(get_users_service),
    current_user: User = Depends(get_current_user),
):
    return service.update(user_id, user_data, current_user)


@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los usuarios activos",
)
def get_all_users(
    pagination: Pagination,
    service: UsersService = Depends(get_users_service),
    current_user: User = Depends(get_current_user),
):
    return service.list(pagination.skip, pagination.limit)

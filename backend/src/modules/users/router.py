from fastapi import APIRouter, Depends, Header, status

from src.core.dependencies import get_current_user, require_admin
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
    responses={
        401: {"description": "Sesión ausente o inválida"},
        403: {"description": "Se requieren permisos de administrador"},
        409: {"description": "El email ya está registrado"},
        404: {"description": "El rol indicado no existe"},
    },
)
def create_new_user(
    user_data: UserCreate,
    service: UsersService = Depends(get_users_service),
    current_user: User = Depends(require_admin),
):
    """Crea un usuario con contraseña temporal.

    Solo administradores (403). El rol indicado debe existir (404) y el email
    no puede estar registrado (409). Se envía un correo de bienvenida con la
    contraseña temporal; si el envío falla, la cuenta queda creada y el fallo
    se registra en los logs sin exponer la contraseña. La acción se audita con
    el id del administrador que la realizó.
    """
    return service.create(user_data, current_user)


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
    service: UsersService = Depends(get_users_service),
    current_user: User = Depends(get_current_user),
):
    return service.list()

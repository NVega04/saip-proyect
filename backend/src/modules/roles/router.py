from fastapi import APIRouter, Depends, status

from src.core.dependencies import get_current_user
from src.modules.roles.dependencies import get_roles_service
from src.modules.roles.schemas import RoleCreate, RolePublic, RoleResponse, RoleUpdate
from src.modules.roles.service import RolesService
from src.modules.users.models import User

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo rol",
    responses={
        401: {"description": "Sesión ausente o inválida"},
        409: {"description": "Ya existe un rol con ese nombre"},
    },
)
def create_role(
    role_data: RoleCreate,
    service: RolesService = Depends(get_roles_service),
    current_user: User = Depends(get_current_user),
):
    """Crea un rol en estado ``active``.

    Exige sesión; el nombre no puede repetirse (409). Los módulos asignables
    se configuran después con ``POST /role-modules/{role_id}``, que sí exige
    permisos de administrador. La creación se audita con el actor.
    """
    return service.create_role(role_data, current_user)


@router.patch(
    "/{role_id}",
    response_model=RolePublic,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un rol",
    responses={
        404: {"description": "Rol no encontrado"},
        409: {"description": "Ya existe ese rol con ese nombre"},
        410: {"description": "El rol esta desactivado"},
        403: {"description": "No se puede modificar un rol protegido"},
    },
)
def updated_role(
    role_id: int,
    role_data: RoleUpdate,
    service: RolesService = Depends(get_roles_service),
    current_user: User = Depends(get_current_user),
):
    return service.update_role(role_id, role_data, current_user)


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar un rol",
    responses={
        404: {"description": "Rol no encontrado"},
        409: {
            "description": "No se puede desactivar: hay usuarios asignados o es rol protegido"
        },
        410: {"description": "El rol ya esta desactivado"},
    },
)
def desactivate_role(
    role_id: int,
    service: RolesService = Depends(get_roles_service),
    current_user: User = Depends(get_current_user),
):
    service.deactivate_role(role_id, current_user)
    return None


@router.get(
    "/",
    response_model=list[RolePublic],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los roles",
)
def get_roles(
    service: RolesService = Depends(get_roles_service),
    current_user: User = Depends(get_current_user),
):
    return service.list_roles()

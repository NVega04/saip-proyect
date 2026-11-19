from fastapi import APIRouter, Depends, status

from src.core.dependencies import get_current_user, require_admin
from src.modules.roles.dependencies import get_role_modules_service
from src.modules.roles.schemas import (
    ModuleResponse,
    RoleModuleAssign,
    RoleModuleResponse,
)
from src.modules.roles.service import RoleModulesService
from src.modules.users.models import User

router = APIRouter(prefix="/role-modules", tags=["Role Modules"])


@router.get(
    "/modules",
    response_model=list[ModuleResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los módulos disponibles",
)
def get_all_modules(
    service: RoleModulesService = Depends(get_role_modules_service),
    current_user: User = Depends(get_current_user),
):
    return service.list_modules()


@router.get(
    "/{role_id}",
    response_model=list[RoleModuleResponse],
    status_code=status.HTTP_200_OK,
    summary="Ver módulos asignados a un rol",
)
def get_role_modules(
    role_id: int,
    service: RoleModulesService = Depends(get_role_modules_service),
    current_user: User = Depends(get_current_user),
):
    return service.list_role_modules(role_id)


@router.post(
    "/{role_id}",
    response_model=list[RoleModuleResponse],
    status_code=status.HTTP_200_OK,
    summary="Asignar módulos a un rol (reemplaza los existentes)",
)
def assign_modules(
    role_id: int,
    data: RoleModuleAssign,
    service: RoleModulesService = Depends(get_role_modules_service),
    current_user: User = Depends(require_admin),
):
    return service.assign_modules(role_id, data, current_user)

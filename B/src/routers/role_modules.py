from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from src.database import get_session
from src.models.models import RoleModule, Role, Module, User
from src.dependencies import get_current_user, require_admin
from src.schemas.schemas import RoleModuleAssign, RoleModuleResponse, ModuleResponse

router = APIRouter(prefix="/role-modules", tags=["Role Modules"])


@router.get(
    "/modules",
    response_model=list[ModuleResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los módulos disponibles",
)
def get_all_modules(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    modules = session.exec(select(Module)).all()
    return modules


@router.get(
    "/{role_id}",
    response_model=list[RoleModuleResponse],
    status_code=status.HTTP_200_OK,
    summary="Ver módulos asignados a un rol",
)
def get_role_modules(
    role_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    role = session.get(Role, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El rol con id '{role_id}' no existe.",
        )

    role_modules = session.exec(
        select(RoleModule).where(RoleModule.role_id == role_id)
    ).all()

    return role_modules


@router.post(
    "/{role_id}",
    response_model=list[RoleModuleResponse],
    status_code=status.HTTP_200_OK,
    summary="Asignar módulos a un rol (reemplaza los existentes)",
)
def assign_modules(
    role_id: int,
    data: RoleModuleAssign,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    # 1. Verificar que el rol existe
    role = session.get(Role, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El rol con id '{role_id}' no existe.",
        )

    # 2. Eliminar módulos anteriores
    old_modules = session.exec(
        select(RoleModule).where(RoleModule.role_id == role_id)
    ).all()
    for m in old_modules:
        session.delete(m)
    session.flush()

    # 3. Asignar nuevos módulos
    new_modules = []
    for module_id in data.module_ids:
        module = session.get(Module, module_id)
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El módulo con id '{module_id}' no existe.",
            )
        new_role_module = RoleModule(
            role_id=role_id,
            module_id=module_id,
        )
        session.add(new_role_module)
        new_modules.append(new_role_module)

    session.commit()
    for m in new_modules:
        session.refresh(m)

    return new_modules
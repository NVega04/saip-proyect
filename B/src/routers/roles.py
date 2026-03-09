from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timezone

from src.database import get_session
from src.models.models import Role 
from src.schemas.schemas import RoleCreate, RoleResponse

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo rol",
)
def create_role(
    role_data: RoleCreate,
    session: Session = Depends(get_session),
):
    # 1. Verificar que el nombre del rol no esté duplicado
    existing_role = session.exec(
        select(Role).where(Role.name == role_data.name)
    ).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El rol '{role_data.name}' ya existe.",
        )

    # 2. Crear el rol
    new_role = Role(
        name=role_data.name,
        description=role_data.description,
    )

    session.add(new_role)
    session.commit()
    session.refresh(new_role)

    return new_role

    # #- Eliminacion suave 
@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar un rol",
    responses={
        404: {"descripcion": "Rol no encontrado"},
        409: {"descripcion": "No se puede desactivar: hay usuarios asignados o es rol protegido"},
        410: {"descripcion": "El rol ya esta desactivado"},
    }
)
def desactivate_role(
    role_id: int,
    session: Session = Depends(get_session),
):
    # Busacar rol 
    role =session.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    # Ya esta desactivado -- para informar 
    if not role.is_active:
        raise HTTPException(status_code=410, detail="El rol ya esta desactivado")
    # Proteccion de roles del sistema 
    protected = {"admin"}
    if role.name.lower() in protected:
                       raise HTTPException(
                           status_code=status.HTTP_403_FORBIDDEN,
                           detail=f"No se puede desactivar el rol de sistema '{role.name}'"
                       )
    # Realizar soft delete
    role.is_active = False
    role.deleted_at = datetime.now(timezone.utc)

    session.add(role) # persistir cambios
    session.commit()

    return None # 204 No content
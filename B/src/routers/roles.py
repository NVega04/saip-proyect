from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timezone

from src.dependencies import get_current_user
from src.database import get_session
from src.models.models import Role, RoleStatus, User
from src.schemas.schemas import RoleCreate, RoleResponse, RolePublic, RoleUpdate

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
        status=RoleStatus.ACTIVE,
    )

    session.add(new_role)
    session.commit()
    session.refresh(new_role)

    return new_role


@router.patch(
    "/{role_id}",
    response_model=RolePublic,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un rol",
    responses={
           404: {"description": "Rol no encontrado"},
           409: {"descripcion": "Ya existe ese rol con ese nombre"},
           410: {"descripcion": "El rol esta desactivado"},
           403: {"descripcion": "No se puede modificar un rol protegido"},
    }
)
def updated_role(
    role_id: int,
    role_data: RoleUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # buscar rol
    role = session.get(Role, role_id)
    if role is None:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
       
    # No se puede editar un rol desactivado
    if role.status == RoleStatus.INACTIVE:
            raise HTTPException(status_code=410, detail="No se puede modificar un rol desactivado")
       
    # Proteccion de roles del sistema 
    protected = {"admin"}
    if role.name.lower() in protected:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No se puede modificar el rol de sistema '{role.name}'"
            )
    # Verificar nombre duplicado si se está cambiando
    if role_data.name is not None and role_data.name.lower() != role.name.lower():
            existing = session.exec(
                    select(Role).where(Role.name == role_data.name)
            ).first()
            if existing:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Ya exixte un rol con el nombre '{role_data.name}'"
                    )
    # Aplicar solo los campos enviados (PATCH parcial)
    update_fields = role_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(role, field, value)
    
    role.updated_at = datetime.now(timezone.utc)   
    role.updated_by = current_user.id          

    session.add(role)
    session.commit()
    session.refresh(role)
        
    return role

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
    current_user: User = Depends(get_current_user),
):
    # Busacar rol 
    role =session.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    # Ya esta desactivado -- para informar 
    if role.status == RoleStatus.INACTIVE:
        raise HTTPException(status_code=410, detail="El rol ya esta desactivado")
    # Proteccion de roles del sistema 
    protected = {"admin"}
    if role.name.lower() in protected:
                       raise HTTPException(
                           status_code=status.HTTP_403_FORBIDDEN,
                           detail=f"No se puede desactivar el rol de sistema '{role.name}'"
                       )
    # Realizar soft delete
    role.status = RoleStatus.INACTIVE
    role.deleted_at = datetime.now(timezone.utc)
    role.deleted_by = current_user.id 

    session.add(role) # persistir cambios
    session.commit()

    return None # 204 No content
    
@router.get(
    "/",
    response_model=list[RolePublic],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los roles",
)
def get_roles(
       session: Session = Depends(get_session),
       current_user: User = Depends(get_current_user),
):
       roles = session.exec(
              select(Role)
       ).all()
       return roles 
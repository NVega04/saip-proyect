from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

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
    

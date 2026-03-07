from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
import logging

from src.database import get_session
from src.models.models import User, Role
from src.schemas.schemas import UserCreate, UserResponse
from src.security import hash_password, generate_temp_password

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Crear nuevo usuario",)

def create_new_user(user_data: UserCreate, session: Session = Depends(get_session)):
    # 1. Verificar que el role_id existe
    role = session.get(Role, user_data.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El rol con id '{user_data.role_id}' no existe.",
        )

    # 2. Verificar que el email no esté registrado
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El email '{user_data.email}' ya está registrado.",
        )

    # 3. Generar y hashear password temporal
    temp_password = generate_temp_password()
    hashed = hash_password(temp_password)

    # 4. Loggear la password temporal (solo una vez, nunca se vuelve a exponer)
    logger.warning(
        f"[SAIP] Password temporal generada para '{user_data.email}': {temp_password}"
    )

    # 5. Crear el usuario
    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        position=user_data.position,
        phone=user_data.phone,
        role_id=user_data.role_id,
        is_admin=user_data.is_admin,
        password_hash=hashed,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
import logging
from src.database import get_session
from src.models.models import User, Role, Session, UserStatus
from src.schemas.schemas import UserCreate, UserResponse, DeleteResponseUser
from src.security import hash_password, generate_temp_password
from datetime import datetime, timezone
from src.dependencies import get_current_user

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

@router.delete("/{user_id}", response_model=DeleteResponseUser, status_code=status.HTTP_200_OK, summary="Eliminar usuario (soft delete)")

def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El usuario con id '{user_id}' no existe.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El usuario con id '{user_id}' ya fue eliminado.",
        )

    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se puede eliminar a un administrador.",
        )

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminarte a ti mismo.",
        )

    now = datetime.now(timezone.utc)
    user.is_active = False
    user.deleted_at = now
    user.deleted_by = current_user.id
    user.status = UserStatus.INACTIVE

    active_sessions = session.exec(
        select(Session).where(
            Session.user_id == user_id,
            Session.is_active == True,
        )
    ).all()
    for s in active_sessions:
        s.is_active = False
        session.add(s)

    session.add(user)
    session.commit()

    return DeleteResponseUser(
        message=f"Usuario '{user.email}' eliminado correctamente.",
        deleted_at=now,
        deleted_by=current_user.id,
    )
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
import logging
from src.database import get_session
from src.models.models import User, Role, UserStatus, SessionApp
from src.schemas.schemas import UserCreate, UserResponse, DeleteResponseUser, UserUpdateResponse, UserUpdate
from src.security import hash_password, generate_temp_password
from datetime import datetime, timezone
from src.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Crear nuevo usuario")
def create_new_user(user_data: UserCreate, session: Session = Depends(get_session)):
    role = session.get(Role, user_data.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El rol con id '{user_data.role_id}' no existe.",
        )

    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El email '{user_data.email}' ya está registrado.",
        )

    temp_password = generate_temp_password()
    hashed = hash_password(temp_password)

    logger.warning(
        f"[SAIP] Password temporal generada para '{user_data.email}': {temp_password}"
    )

    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        phone=user_data.phone,
        role_id=user_data.role_id,
        is_admin=user_data.is_admin,
        password_hash=hashed,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user

@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK, summary="Obtener usuario autenticado")
def get_me(
    current_user: User = Depends(get_current_user),
):
    
    return current_user
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

    if user.status == UserStatus.INACTIVE:
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
    user.deleted_at = now
    user.deleted_by = current_user.id
    user.status = UserStatus.INACTIVE

    active_sessions = session.exec(
        select(SessionApp).where(
            SessionApp.user_id == user_id,
            SessionApp.is_active == True,
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


@router.put("/{user_id}", response_model=UserUpdateResponse, status_code=status.HTTP_200_OK, summary="Actualizar usuario")
def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El usuario con id '{user_id}' no existe.",
        )

    if user.status == UserStatus.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El usuario con id '{user_id}' está inactivo.",
        )

    if user_data.email and user_data.email != user.email:
        existing = session.exec(
            select(User).where(User.email == user_data.email)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El email '{user_data.email}' ya está registrado.",
            )

    if user_data.role_id:
        role = session.get(Role, user_data.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El rol con id '{user_data.role_id}' no existe.",
            )

    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.now(timezone.utc)
    user.updated_by = current_user.id

    session.add(user)
    session.commit()
    session.refresh(user)

    return user

@router.get("/", response_model=list[UserResponse], status_code=status.HTTP_200_OK, summary="Listar todos los usuarios activos",)
def get_all_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    users = session.exec(
        select(User)
    ).all()
    return users


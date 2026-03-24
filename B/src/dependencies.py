from fastapi import Depends, HTTPException, status, Header
from sqlmodel import Session, select
from datetime import datetime, timezone

from src.database import get_session
from src.models.models import SessionApp, User, RoleModule, Module

def get_current_user(
    session_token: str = Header(..., alias="session_token"),
    session: Session = Depends(get_session),
) -> User:

# Buscar la sesión por token
    user_session = session.exec(
        select(SessionApp).where(SessionApp.token == session_token)  # ← buscar por token en lugar de PK
    ).first()
    if user_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión no encontrada"
        )
    if datetime.now(timezone.utc) > user_session.expires_at.replace(tzinfo=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada"
        )
    if not user_session.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inactiva"
        )

    return user_session.user

def require_module(module_name: str):
    def checker(
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session),
    ) -> User:
        if current_user.is_admin:
            return current_user

        access = session.exec(
            select(RoleModule)
            .join(Module, RoleModule.module_id == Module.id)
            .where(
                RoleModule.role_id == current_user.role_id,
                Module.name == module_name,
            )
        ).first()

        if not access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes acceso al módulo '{module_name}'.",
            )
        return current_user
    return checker


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador.",
        )
    return current_user
from fastapi import Depends, HTTPException, status, Header
from sqlmodel import Session, select
from datetime import datetime, timezone

from src.database import get_session
from src.models.models import SessionApp, User

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
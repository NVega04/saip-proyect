from fastapi import Depends, HTTPException, status, Header
from sqlmodel import Session
from datetime import datetime, timezone

from src.database import get_session
from src.models.models import Session as UserSession, User

def get_current_user(
    session_token: str = Header(...),           # viene en el header de la request
    session: Session = Depends(get_session),
) -> User:
    # Buscar la sesión
    user_session = session.get(UserSession, session_token)
    if user_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión no encontrada"
        )
    # Validar que no haya expirado
    if datetime.now(timezone.utc) > user_session.expires_at.replace(tzinfo=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada"
        )
    # Validar que esté activa
    if not user_session.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inactiva"
        )

    return user_session.user
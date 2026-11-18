from fastapi import Depends
from sqlmodel import Session

from src.core.database import get_session
from src.modules.auth.service import AuthService


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    return AuthService(session)

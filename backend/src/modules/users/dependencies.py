from fastapi import Depends
from sqlmodel import Session

from src.core.database import get_session
from src.modules.users.service import UsersService


def get_users_service(session: Session = Depends(get_session)) -> UsersService:
    return UsersService(session)

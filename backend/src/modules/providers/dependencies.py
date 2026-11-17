from fastapi import Depends
from sqlmodel import Session

from src.core.database import get_session
from src.modules.providers.service import ProvidersService


def get_providers_service(session: Session = Depends(get_session)) -> ProvidersService:
    return ProvidersService(session)

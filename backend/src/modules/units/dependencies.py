from fastapi import Depends
from sqlmodel import Session

from src.core.database import get_session
from src.modules.units.service import UnitsService


def get_units_service(session: Session = Depends(get_session)) -> UnitsService:
    return UnitsService(session)

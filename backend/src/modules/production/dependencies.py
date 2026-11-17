from fastapi import Depends
from sqlmodel import Session

from src.core.database import get_session
from src.modules.production.service import ProductionService


def get_production_service(
    session: Session = Depends(get_session),
) -> ProductionService:
    return ProductionService(session)

from fastapi import Depends
from sqlmodel import Session

from src.core.database import get_session
from src.modules.sales.service import SalesService


def get_sales_service(session: Session = Depends(get_session)) -> SalesService:
    return SalesService(session)

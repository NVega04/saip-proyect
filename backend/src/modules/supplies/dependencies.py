from fastapi import Depends
from sqlmodel import Session

from src.core.database import get_session
from src.modules.supplies.categories_service import SupplyCategoriesService
from src.modules.supplies.service import SuppliesService


def get_supplies_service(session: Session = Depends(get_session)) -> SuppliesService:
    return SuppliesService(session)


def get_supply_categories_service(
    session: Session = Depends(get_session),
) -> SupplyCategoriesService:
    return SupplyCategoriesService(session)

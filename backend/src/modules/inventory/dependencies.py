from fastapi import Depends
from sqlmodel import Session

from src.core.database import get_session
from src.modules.inventory.service import InventoryService


def get_inventory_service(
    session: Session = Depends(get_session),
) -> InventoryService:
    return InventoryService(session)

from fastapi import Depends
from sqlmodel import Session

from src.core.database import get_session
from src.modules.products.service import ProductsService


def get_products_service(session: Session = Depends(get_session)) -> ProductsService:
    return ProductsService(session)

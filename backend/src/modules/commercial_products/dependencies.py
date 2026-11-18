from fastapi import Depends
from sqlmodel import Session

from src.core.database import get_session
from src.modules.commercial_products.categories_service import (
    ProductCategoriesService,
)
from src.modules.commercial_products.service import CommercialProductsService


def get_commercial_products_service(
    session: Session = Depends(get_session),
) -> CommercialProductsService:
    return CommercialProductsService(session)


def get_product_categories_service(
    session: Session = Depends(get_session),
) -> ProductCategoriesService:
    return ProductCategoriesService(session)

from datetime import datetime

from sqlmodel import Session, select

from src.core.exceptions import ConflictError, NotFoundError
from src.core.time import BOGOTA_TZ
from src.modules.commercial_products.models import ProductCategory
from src.modules.commercial_products.schemas import (
    DeleteResponseProductCategory,
    ProductCategoryCreate,
    ProductCategoryUpdate,
)
from src.modules.users.models import User


class ProductCategoriesService:
    def __init__(self, session: Session):
        self.session = session

    def list(self, skip: int = 0, limit: int = 20) -> list[ProductCategory]:
        return self.session.exec(
            select(ProductCategory).offset(skip).limit(limit)
        ).all()

    def get(self, category_id: int) -> ProductCategory:
        category = self.session.get(ProductCategory, category_id)
        if not category:
            raise NotFoundError("Categoría no encontrada.")
        return category

    def create(
        self, data: ProductCategoryCreate, current_user: User
    ) -> ProductCategory:
        existing = self.session.exec(
            select(ProductCategory).where(ProductCategory.name == data.name)
        ).first()
        if existing:
            raise ConflictError(f"La categoría '{data.name}' ya existe.")

        new_category = ProductCategory(
            name=data.name,
            description=data.description,
            created_by=current_user.id,
        )
        self.session.add(new_category)
        self.session.commit()
        self.session.refresh(new_category)
        return new_category

    def update(
        self, category_id: int, data: ProductCategoryUpdate, current_user: User
    ) -> ProductCategory:
        category = self.get(category_id)

        if data.name and data.name != category.name:
            existing = self.session.exec(
                select(ProductCategory).where(ProductCategory.name == data.name)
            ).first()
            if existing:
                raise ConflictError(f"El nombre '{data.name}' ya está en uso.")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        category.updated_at = datetime.now(BOGOTA_TZ)
        category.updated_by = current_user.id
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def delete(
        self, category_id: int, current_user: User
    ) -> DeleteResponseProductCategory:
        category = self.get(category_id)

        if category.status == "inactive":
            raise ConflictError("La categoría ya fue eliminada.")

        now = datetime.now(BOGOTA_TZ)
        category.deleted_at = now
        category.deleted_by = current_user.id
        category.status = "inactive"
        self.session.add(category)
        self.session.commit()

        return DeleteResponseProductCategory(
            message=f"Categoría '{category.name}' eliminada correctamente.",
            deleted_at=now,
            deleted_by=current_user.id,
        )

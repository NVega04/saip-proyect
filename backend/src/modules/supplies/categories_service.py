from datetime import datetime, timezone

from sqlmodel import Session, select

from src.core.exceptions import ConflictError, NotFoundError
from src.modules.supplies.models import SupplyCategory
from src.modules.supplies.schemas import (
    DeleteResponseSupplyCategory,
    SupplyCategoryCreate,
    SupplyCategoryUpdate,
)
from src.modules.users.models import User


class SupplyCategoriesService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: SupplyCategoryCreate, current_user: User) -> SupplyCategory:
        existing = self.session.exec(
            select(SupplyCategory).where(SupplyCategory.name == data.name)
        ).first()
        if existing:
            raise ConflictError(f"La categoría '{data.name}' ya existe.")

        new_category = SupplyCategory(
            name=data.name,
            description=data.description,
            created_by=current_user.id,
        )
        self.session.add(new_category)
        self.session.commit()
        self.session.refresh(new_category)
        return new_category

    def list(self, skip: int = 0, limit: int = 20) -> list[SupplyCategory]:
        return self.session.exec(
            select(SupplyCategory).offset(skip).limit(limit)
        ).all()

    def get(self, category_id: int) -> SupplyCategory:
        category = self.session.get(SupplyCategory, category_id)
        if not category:
            raise NotFoundError(f"La categoría con id '{category_id}' no existe.")
        return category

    def update(
        self, category_id: int, data: SupplyCategoryUpdate, current_user: User
    ) -> SupplyCategory:
        category = self.get(category_id)

        if data.name and data.name != category.name:
            existing = self.session.exec(
                select(SupplyCategory).where(SupplyCategory.name == data.name)
            ).first()
            if existing:
                raise ConflictError(f"El nombre '{data.name}' ya está en uso.")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        category.updated_at = datetime.now(timezone.utc)
        category.updated_by = current_user.id

        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def delete(
        self, category_id: int, current_user: User
    ) -> DeleteResponseSupplyCategory:
        category = self.get(category_id)

        if category.status == "inactive":
            raise ConflictError(
                f"La categoría con id '{category_id}' ya fue eliminada."
            )

        now = datetime.now(timezone.utc)
        category.deleted_at = now
        category.deleted_by = current_user.id
        category.status = "inactive"

        self.session.add(category)
        self.session.commit()

        return DeleteResponseSupplyCategory(
            message=f"Categoría '{category.name}' eliminada correctamente.",
            deleted_at=now,
            deleted_by=current_user.id,
        )

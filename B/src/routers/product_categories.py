from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from zoneinfo import ZoneInfo

from src.database import get_session
from src.models.models import ProductCategory, User
from src.schemas.schemas import (
    ProductCategoryCreate,
    ProductCategoryUpdate,
    ProductCategoryResponse,
    DeleteResponseProductCategory,
)
from src.dependencies import get_current_user

router = APIRouter(prefix="/product-categories", tags=["ProductCategories"])

BOGOTA_TZ = ZoneInfo("America/Bogota")


@router.get("/", response_model=list[ProductCategoryResponse], status_code=status.HTTP_200_OK)
def get_all(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(ProductCategory)).all()


@router.get("/{category_id}", response_model=ProductCategoryResponse, status_code=status.HTTP_200_OK)
def get_one(category_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    category = session.get(ProductCategory, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada.")
    return category


@router.post("/", response_model=ProductCategoryResponse, status_code=status.HTTP_201_CREATED)
def create(data: ProductCategoryCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    existing = session.exec(select(ProductCategory).where(ProductCategory.name == data.name)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La categoría '{data.name}' ya existe.")

    new_category = ProductCategory(
        name=data.name,
        description=data.description,
        created_by=current_user.id,
    )
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    return new_category


@router.put("/{category_id}", response_model=ProductCategoryResponse, status_code=status.HTTP_200_OK)
def update(category_id: int, data: ProductCategoryUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    category = session.get(ProductCategory, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada.")

    if data.name and data.name != category.name:
        existing = session.exec(select(ProductCategory).where(ProductCategory.name == data.name)).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El nombre '{data.name}' ya está en uso.")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    category.updated_at = datetime.now(BOGOTA_TZ)
    category.updated_by = current_user.id
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.delete("/{category_id}", response_model=DeleteResponseProductCategory, status_code=status.HTTP_200_OK)
def delete(category_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    category = session.get(ProductCategory, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada.")

    if category.status == "inactive":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La categoría ya fue eliminada.")

    now = datetime.now(BOGOTA_TZ)
    category.deleted_at = now
    category.deleted_by = current_user.id
    category.status = "inactive"
    session.add(category)
    session.commit()

    return DeleteResponseProductCategory(
        message=f"Categoría '{category.name}' eliminada correctamente.",
        deleted_at=now,
        deleted_by=current_user.id,
    )
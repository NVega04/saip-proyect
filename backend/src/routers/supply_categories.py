from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timezone

from src.database import get_session
from src.models.models import User, SupplyCategory
from src.schemas.schemas import (
    SupplyCategoryCreate,
    SupplyCategoryResponse,
    SupplyCategoryUpdate,
    DeleteResponseSupplyCategory,
)
from src.dependencies import get_current_user

router = APIRouter(prefix="/supply-categories", tags=["SupplyCategories"])


@router.post(
    "/",
    response_model=SupplyCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva categoría de insumo",
)
def create_supply_category(
    data: SupplyCategoryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    existing = session.exec(
        select(SupplyCategory).where(SupplyCategory.name == data.name)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La categoría '{data.name}' ya existe.",
        )

    new_category = SupplyCategory(
        name=data.name,
        description=data.description,
        created_by=current_user.id,
    )

    session.add(new_category)
    session.commit()
    session.refresh(new_category)

    return new_category


@router.get(
    "/",
    response_model=list[SupplyCategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todas las categorías de insumos",
)
def get_all_supply_categories(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    categories = session.exec(select(SupplyCategory)).all()
    return categories


@router.get(
    "/{category_id}",
    response_model=SupplyCategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener categoría de insumo por ID",
)
def get_supply_category(
    category_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    category = session.get(SupplyCategory, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La categoría con id '{category_id}' no existe.",
        )
    return category


@router.put(
    "/{category_id}",
    response_model=SupplyCategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar categoría de insumo",
)
def update_supply_category(
    category_id: int,
    data: SupplyCategoryUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    category = session.get(SupplyCategory, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La categoría con id '{category_id}' no existe.",
        )

    if data.name and data.name != category.name:
        existing = session.exec(
            select(SupplyCategory).where(SupplyCategory.name == data.name)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El nombre '{data.name}' ya está en uso.",
            )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    category.updated_at = datetime.now(timezone.utc)
    category.updated_by = current_user.id

    session.add(category)
    session.commit()
    session.refresh(category)

    return category


@router.delete(
    "/{category_id}",
    response_model=DeleteResponseSupplyCategory,
    status_code=status.HTTP_200_OK,
    summary="Eliminar categoría de insumo (soft delete)",
)
def delete_supply_category(
    category_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    category = session.get(SupplyCategory, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La categoría con id '{category_id}' no existe.",
        )

    if category.status == "inactive":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La categoría con id '{category_id}' ya fue eliminada.",
        )

    now = datetime.now(timezone.utc)
    category.deleted_at = now
    category.deleted_by = current_user.id
    category.status = "inactive"

    session.add(category)
    session.commit()

    return DeleteResponseSupplyCategory(
        message=f"Categoría '{category.name}' eliminada correctamente.",
        deleted_at=now,
        deleted_by=current_user.id,
    )

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timezone

from src.database import get_session
from src.models.models import Supply, SupplyCategory, Unit, User
from src.schemas.schemas import (
    SupplyCreate,
    SupplyResponse,
    SupplyUpdate,
    DeleteResponseSupply,
)
from src.dependencies import get_current_user

router = APIRouter(prefix="/supplies", tags=["Supplies"])


@router.post(
    "/",
    response_model=SupplyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo insumo",
)
def create_supply(
    data: SupplyCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    category = session.get(SupplyCategory, data.category_id)
    if not category or category.status == "inactive":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La categoría con id '{data.category_id}' no existe.",
        )

    unit = session.get(Unit, data.unit_id)
    if not unit or unit.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La unidad con id '{data.unit_id}' no existe.",
        )

    existing = session.exec(
        select(Supply).where(
            Supply.name == data.name,
            Supply.deleted_at == None,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un insumo con el nombre '{data.name}'.",
        )

    new_supply = Supply(
        name=data.name,
        description=data.description,
        category_id=data.category_id,
        unit_id=data.unit_id,
        available_quantity=data.available_quantity,
        min_stock=data.min_stock,
        max_stock=data.max_stock,
        supplier_id=data.supplier_id,
        expiration_date=data.expiration_date,
        created_by=current_user.id,
    )

    session.add(new_supply)
    session.commit()
    session.refresh(new_supply)

    return new_supply


@router.get(
    "/",
    response_model=list[SupplyResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los insumos activos",
)
def get_all_supplies(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    supplies = session.exec(select(Supply).where(Supply.deleted_at == None)).all()
    return supplies


@router.get(
    "/{supply_id}",
    response_model=SupplyResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener insumo por ID",
)
def get_supply(
    supply_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    supply = session.get(Supply, supply_id)
    if not supply or supply.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El insumo con id '{supply_id}' no existe.",
        )
    return supply


@router.put(
    "/{supply_id}",
    response_model=SupplyResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar insumo",
)
def update_supply(
    supply_id: int,
    data: SupplyUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    supply = session.get(Supply, supply_id)
    if not supply or supply.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El insumo con id '{supply_id}' no existe.",
        )

    if data.name and data.name != supply.name:
        existing = session.exec(
            select(Supply).where(
                Supply.name == data.name,
                Supply.id != supply_id,
                Supply.deleted_at == None,
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un insumo con el nombre '{data.name}'.",
            )

    if data.category_id is not None:
        category = session.get(SupplyCategory, data.category_id)
        if not category or category.status == "inactive":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La categoría con id '{data.category_id}' no existe.",
            )

    if data.unit_id is not None:
        unit = session.get(Unit, data.unit_id)
        if not unit or unit.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La unidad con id '{data.unit_id}' no existe.",
            )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supply, field, value)

    supply.updated_at = datetime.now(timezone.utc)
    supply.updated_by = current_user.id

    session.add(supply)
    session.commit()
    session.refresh(supply)

    return supply


@router.delete(
    "/{supply_id}",
    response_model=DeleteResponseSupply,
    status_code=status.HTTP_200_OK,
    summary="Eliminar insumo (soft delete)",
)
def delete_supply(
    supply_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    supply = session.get(Supply, supply_id)
    if not supply:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El insumo con id '{supply_id}' no existe.",
        )

    if supply.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El insumo con id '{supply_id}' ya fue eliminado.",
        )

    now = datetime.now(timezone.utc)
    supply.deleted_at = now
    supply.deleted_by = current_user.id
    supply.status = "inactive"

    session.add(supply)
    session.commit()

    return DeleteResponseSupply(
        message=f"Insumo '{supply.name}' eliminado correctamente.",
        deleted_at=now,
        deleted_by=current_user.id,
    )

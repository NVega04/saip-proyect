from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timezone

from src.database import get_session
from src.models.models import Unit, User
from src.schemas.schemas import UnitCreate, UnitUpdate, UnitResponse
from src.dependencies import get_current_user

router = APIRouter(prefix="/units", tags=["Units"])


@router.get("/", response_model=list[UnitResponse], status_code=status.HTTP_200_OK)
def get_units(
    session: Session = Depends(get_session),
):
    units = session.exec(select(Unit).where(Unit.deleted_at == None)).all()
    return units


@router.get("/{unit_id}", response_model=UnitResponse, status_code=status.HTTP_200_OK)
def get_unit(
    unit_id: int,
    session: Session = Depends(get_session),
):
    unit = session.get(Unit, unit_id)
    if not unit or unit.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidad no encontrada",
        )
    return unit


@router.post("/", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
def create_unit(
    unit_data: UnitCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    existing = session.exec(
        select(Unit).where(
            (Unit.name == unit_data.name)
            | (Unit.abbreviation == unit_data.abbreviation),
            Unit.deleted_at == None,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una unidad con ese nombre o abreviatura",
        )

    new_unit = Unit(
        name=unit_data.name,
        abbreviation=unit_data.abbreviation,
        description=unit_data.description,
        quantity=unit_data.quantity,
        created_by=current_user.id,
    )

    session.add(new_unit)
    session.commit()
    session.refresh(new_unit)

    return new_unit


@router.patch("/{unit_id}", response_model=UnitResponse, status_code=status.HTTP_200_OK)
def update_unit(
    unit_id: int,
    unit_data: UnitUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    unit = session.get(Unit, unit_id)
    if not unit or unit.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidad no encontrada",
        )

    if unit_data.name is not None and unit_data.name != unit.name:
        existing = session.exec(
            select(Unit).where(
                Unit.name == unit_data.name,
                Unit.id != unit_id,
                Unit.deleted_at == None,
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una unidad con ese nombre",
            )

    if (
        unit_data.abbreviation is not None
        and unit_data.abbreviation != unit.abbreviation
    ):
        existing = session.exec(
            select(Unit).where(
                Unit.abbreviation == unit_data.abbreviation,
                Unit.id != unit_id,
                Unit.deleted_at == None,
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una unidad con esa abreviatura",
            )

    update_fields = unit_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(unit, field, value)

    unit.updated_at = datetime.now(timezone.utc)
    unit.updated_by = current_user.id

    session.add(unit)
    session.commit()
    session.refresh(unit)

    return unit


@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(
    unit_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    unit = session.get(Unit, unit_id)
    if not unit or unit.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidad no encontrada",
        )

    unit.deleted_at = datetime.now(timezone.utc)
    unit.deleted_by = current_user.id

    session.add(unit)
    session.commit()

    return None

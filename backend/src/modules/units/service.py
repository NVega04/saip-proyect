from datetime import datetime, timezone

from sqlmodel import Session, select

from src.core.exceptions import ConflictError, NotFoundError
from src.modules.units.models import Unit
from src.modules.units.schemas import UnitCreate, UnitUpdate
from src.modules.users.models import User


class UnitsService:
    def __init__(self, session: Session):
        self.session = session

    def list_units(self, skip: int = 0, limit: int = 20) -> list[Unit]:
        return self.session.exec(
            select(Unit).where(Unit.deleted_at == None).offset(skip).limit(limit)
        ).all()

    def get_unit(self, unit_id: int) -> Unit:
        unit = self.session.get(Unit, unit_id)
        if not unit or unit.deleted_at is not None:
            raise NotFoundError("Unidad no encontrada")
        return unit

    def create_unit(self, data: UnitCreate, current_user: User) -> Unit:
        existing = self.session.exec(
            select(Unit).where(
                (Unit.name == data.name) | (Unit.abbreviation == data.abbreviation),
                Unit.deleted_at == None,
            )
        ).first()
        if existing:
            raise ConflictError("Ya existe una unidad con ese nombre o abreviatura")

        unit = Unit(
            name=data.name,
            abbreviation=data.abbreviation,
            description=data.description,
            quantity=data.quantity,
            created_by=current_user.id,
        )
        self.session.add(unit)
        self.session.commit()
        self.session.refresh(unit)
        return unit

    def update_unit(self, unit_id: int, data: UnitUpdate, current_user: User) -> Unit:
        unit = self.get_unit(unit_id)

        if data.name is not None and data.name != unit.name:
            existing = self.session.exec(
                select(Unit).where(
                    Unit.name == data.name,
                    Unit.id != unit_id,
                    Unit.deleted_at == None,
                )
            ).first()
            if existing:
                raise ConflictError("Ya existe una unidad con ese nombre")

        if data.abbreviation is not None and data.abbreviation != unit.abbreviation:
            existing = self.session.exec(
                select(Unit).where(
                    Unit.abbreviation == data.abbreviation,
                    Unit.id != unit_id,
                    Unit.deleted_at == None,
                )
            ).first()
            if existing:
                raise ConflictError("Ya existe una unidad con esa abreviatura")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(unit, field, value)

        unit.updated_at = datetime.now(timezone.utc)
        unit.updated_by = current_user.id

        self.session.add(unit)
        self.session.commit()
        self.session.refresh(unit)
        return unit

    def delete_unit(self, unit_id: int, current_user: User) -> None:
        unit = self.get_unit(unit_id)
        unit.deleted_at = datetime.now(timezone.utc)
        unit.deleted_by = current_user.id
        self.session.add(unit)
        self.session.commit()

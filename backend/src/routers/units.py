from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timezone

from src.database import get_session
from src.models.models import Unit, User
from src.schemas.schemas import UnitCreate, UnitUpdate, UnitResponse
from src.dependencies import get_current_user

router = APIRouter(prefix="/units", tags=["Units"])


def _obtener_unidad_activa_o_404(session: Session, unidad_id: int) -> Unit:
    """Devuelve la unidad activa con el id indicado o lanza 404."""
    unidad = session.get(Unit, unidad_id)
    if not unidad or unidad.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidad no encontrada",
        )
    return unidad


def _buscar_unidad_por_nombre_o_abreviatura(
    session: Session, nombre: str, abreviatura: str
) -> Optional[Unit]:
    """Busca una unidad activa que use el mismo nombre o la misma abreviatura."""
    return session.exec(
        select(Unit).where(
            (Unit.name == nombre) | (Unit.abbreviation == abreviatura),
            Unit.deleted_at == None,
        )
    ).first()


def _buscar_unidad_por_campo(
    session: Session,
    campo: Any,
    valor: str,
    unidad_id_a_excluir: int,
) -> Optional[Unit]:
    """Busca una unidad activa por un campo único (nombre o abreviatura), excluyendo una unidad."""
    return session.exec(
        select(Unit).where(
            campo == valor,
            Unit.id != unidad_id_a_excluir,
            Unit.deleted_at == None,
        )
    ).first()


def _aplicar_actualizacion(
    unidad: Unit,
    datos_unidad: UnitUpdate,
    usuario_actual: User,
) -> None:
    """Aplica los campos enviados y registra la auditoría de actualización."""
    campos_a_actualizar = datos_unidad.model_dump(exclude_unset=True)
    for campo, valor in campos_a_actualizar.items():
        setattr(unidad, campo, valor)

    unidad.updated_at = datetime.now(timezone.utc)
    unidad.updated_by = usuario_actual.id


def _marcar_unidad_eliminada(unidad: Unit, usuario_actual: User) -> None:
    """Registra la eliminación lógica (soft delete) de la unidad."""
    unidad.deleted_at = datetime.now(timezone.utc)
    unidad.deleted_by = usuario_actual.id


@router.get("/", response_model=list[UnitResponse], status_code=status.HTTP_200_OK)
def get_units(
    session: Session = Depends(get_session),
):
    unidades = session.exec(select(Unit).where(Unit.deleted_at == None)).all()
    return unidades


@router.get("/{unit_id}", response_model=UnitResponse, status_code=status.HTTP_200_OK)
def get_unit(
    unit_id: int,
    session: Session = Depends(get_session),
):
    return _obtener_unidad_activa_o_404(session, unit_id)


@router.post("/", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
def create_unit(
    unit_data: UnitCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    unidad_existente = _buscar_unidad_por_nombre_o_abreviatura(
        session, unit_data.name, unit_data.abbreviation
    )
    if unidad_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una unidad con ese nombre o abreviatura",
        )

    nueva_unidad = Unit(
        name=unit_data.name,
        abbreviation=unit_data.abbreviation,
        description=unit_data.description,
        quantity=unit_data.quantity,
        created_by=current_user.id,
    )

    session.add(nueva_unidad)
    session.commit()
    session.refresh(nueva_unidad)

    return nueva_unidad


@router.patch("/{unit_id}", response_model=UnitResponse, status_code=status.HTTP_200_OK)
def update_unit(
    unit_id: int,
    unit_data: UnitUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    unidad = _obtener_unidad_activa_o_404(session, unit_id)

    if unit_data.name is not None and unit_data.name != unidad.name:
        nombre_en_uso = _buscar_unidad_por_campo(
            session, Unit.name, unit_data.name, unit_id
        )
        if nombre_en_uso:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una unidad con ese nombre",
            )

    if (
        unit_data.abbreviation is not None
        and unit_data.abbreviation != unidad.abbreviation
    ):
        abreviatura_en_uso = _buscar_unidad_por_campo(
            session, Unit.abbreviation, unit_data.abbreviation, unit_id
        )
        if abreviatura_en_uso:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una unidad con esa abreviatura",
            )

    _aplicar_actualizacion(unidad, unit_data, current_user)

    session.add(unidad)
    session.commit()
    session.refresh(unidad)

    return unidad


@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(
    unit_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    unidad = _obtener_unidad_activa_o_404(session, unit_id)

    _marcar_unidad_eliminada(unidad, current_user)

    session.add(unidad)
    session.commit()

    return None

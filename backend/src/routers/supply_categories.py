from typing import Optional

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


def _obtener_categoria_o_404(session: Session, categoria_id: int) -> SupplyCategory:
    """Devuelve la categoría de insumo con el id indicado o lanza 404."""
    categoria = session.get(SupplyCategory, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La categoría con id '{categoria_id}' no existe.",
        )
    return categoria


def _buscar_categoria_por_nombre(
    session: Session, nombre: str
) -> Optional[SupplyCategory]:
    """Busca una categoría de insumo con el nombre indicado."""
    return session.exec(
        select(SupplyCategory).where(SupplyCategory.name == nombre)
    ).first()


def _verificar_nombre_disponible(
    session: Session, nombre: str, mensaje_conflicto: str
) -> None:
    """Lanza 409 si ya existe una categoría de insumo con el nombre indicado."""
    categoria_existente = _buscar_categoria_por_nombre(session, nombre)
    if categoria_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=mensaje_conflicto,
        )


def _aplicar_actualizacion(
    categoria: SupplyCategory,
    datos_categoria: SupplyCategoryUpdate,
    usuario_actual: User,
) -> None:
    """Aplica los campos enviados y registra la auditoría de actualización."""
    campos_a_actualizar = datos_categoria.model_dump(exclude_unset=True)
    for campo, valor in campos_a_actualizar.items():
        setattr(categoria, campo, valor)

    categoria.updated_at = datetime.now(timezone.utc)
    categoria.updated_by = usuario_actual.id


def _marcar_categoria_eliminada(
    categoria: SupplyCategory,
    usuario_actual: User,
) -> DeleteResponseSupplyCategory:
    """Registra la eliminación lógica (soft delete) de la categoría."""
    ahora = datetime.now(timezone.utc)
    categoria.deleted_at = ahora
    categoria.deleted_by = usuario_actual.id
    categoria.status = "inactive"

    return DeleteResponseSupplyCategory(
        message=f"Categoría '{categoria.name}' eliminada correctamente.",
        deleted_at=ahora,
        deleted_by=usuario_actual.id,
    )


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
    _verificar_nombre_disponible(
        session,
        data.name,
        mensaje_conflicto=f"La categoría '{data.name}' ya existe.",
    )

    nueva_categoria = SupplyCategory(
        name=data.name,
        description=data.description,
        created_by=current_user.id,
    )

    session.add(nueva_categoria)
    session.commit()
    session.refresh(nueva_categoria)

    return nueva_categoria


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
    categorias = session.exec(select(SupplyCategory)).all()
    return categorias


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
    return _obtener_categoria_o_404(session, category_id)


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
    categoria = _obtener_categoria_o_404(session, category_id)

    if data.name and data.name != categoria.name:
        _verificar_nombre_disponible(
            session,
            data.name,
            mensaje_conflicto=f"El nombre '{data.name}' ya está en uso.",
        )

    _aplicar_actualizacion(categoria, data, current_user)

    session.add(categoria)
    session.commit()
    session.refresh(categoria)

    return categoria


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
    categoria = _obtener_categoria_o_404(session, category_id)

    if categoria.status == "inactive":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La categoría con id '{category_id}' ya fue eliminada.",
        )

    respuesta_eliminacion = _marcar_categoria_eliminada(categoria, current_user)

    session.add(categoria)
    session.commit()

    return respuesta_eliminacion

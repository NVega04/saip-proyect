from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session, select
from datetime import datetime, timezone

from src.database import get_session
from src.models.models import Supply, SupplyCategory, Unit, User
from src.schemas.schemas import (
    SupplyCreate,
    SupplyResponse,
    SupplyUpdate,
    DeleteResponseSupply,
    BulkImportResult,
)
from src.dependencies import get_current_user
from src.bulk.parser import (
    RowError,
    name_key,
    optional_text,
    parse_datetime,
    parse_spreadsheet,
    required,
    run_bulk,
    safe_float,
    template_response,
)

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


# ── Carga masiva ────────────────────────────────────────────────────────────
BULK_SUPPLY_HEADERS = [
    "nombre",
    "descripcion",
    "categoria",
    "unidad",
    "stock_disponible",
    "stock_min",
    "stock_max",
    "fecha_vencimiento",
]
BULK_SUPPLY_EXAMPLES = [
    ["Harina de trigo", "Harina panadera tipo 550", "Insumos basicos", "kg", 25, 10, 100, "2026-12-31"],
]

@router.post(
    "/bulk/import",
    response_model=BulkImportResult,
    status_code=status.HTTP_200_OK,
    summary="Cargar insumos por archivo Excel/CSV",
)
def bulk_import_supplies(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    rows = parse_spreadsheet(file)
    categories = {
        name_key(c.name): c
        for c in session.exec(select(SupplyCategory)).all()
        if c.status == "active"
    }
    units = {
        name_key(u.name): u
        for u in session.exec(select(Unit)).all()
        if u.deleted_at is None
    }
    units_abbr = {name_key(u.abbreviation): u for u in units.values()}

    def process_row(row):
        nombre = required(row, "nombre", "nombre")
        if len(nombre) > 150:
            raise RowError("El nombre supera los 150 caracteres.")
        descripcion = optional_text(row, "descripcion")
        categoria_name = required(row, "categoria", "categoria")
        unidad_name = required(row, "unidad", "unidad")

        category = categories.get(categoria_name)
        if category is None:
            raise RowError(f"No existe la categoría '{row.get('categoria')}'.")

        unit = units.get(unidad_name) or units_abbr.get(unidad_name)
        if unit is None:
            raise RowError(f"No existe la unidad '{row.get('unidad')}'.")

        existing = session.exec(
            select(Supply).where(Supply.name == nombre, Supply.deleted_at == None)
        ).first()
        if existing:
            raise RowError(f"Ya existe un insumo con el nombre '{row.get('nombre')}'.")

        new_supply = Supply(
            name=nombre,
            description=descripcion,
            category_id=category.id,
            unit_id=unit.id,
            available_quantity=safe_float(row.get("stock_disponible"), "stock_disponible"),
            min_stock=safe_float(row.get("stock_min"), "stock_min"),
            max_stock=safe_float(row.get("stock_max"), "stock_max"),
            supplier_id=None,
            expiration_date=parse_datetime(row.get("fecha_vencimiento"), "fecha_vencimiento"),
            created_by=current_user.id,
        )
        session.add(new_supply)
        return False

    return run_bulk(session, rows, process_row)


@router.get(
    "/bulk/template",
    status_code=status.HTTP_200_OK,
    summary="Descargar plantilla de insumos",
)
def bulk_supplies_template():
    return template_response(
        "plantilla_insumos.xlsx", BULK_SUPPLY_HEADERS, BULK_SUPPLY_EXAMPLES
    )

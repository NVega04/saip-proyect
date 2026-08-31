from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlmodel import Session, select
from datetime import datetime, timezone

from src.database import get_session
from src.models.models import Product, ProductStatus, User, Unit
from src.schemas.schemas import ProductCreate, ProductUpdate, ProductResponse, BulkImportResult
from src.dependencies import get_current_user
from src.bulk.parser import (
    RowError,
    name_key,
    optional_text,
    parse_spreadsheet,
    required,
    run_bulk,
    safe_float,
    template_response,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
def get_products(
    session: Session = Depends(get_session),
):
    products = session.exec(select(Product).where(Product.deleted_at == None)).all()
    return products


@router.get(
    "/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK
)
def get_product(
    product_id: int,
    session: Session = Depends(get_session),
):
    product = session.get(Product, product_id)
    if not product or product.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    unit = session.get(Unit, product_data.unit_id)
    if not unit or unit.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidad no encontrada",
        )

    existing = session.exec(
        select(Product).where(
            Product.name == product_data.name,
            Product.deleted_at == None,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un producto con ese nombre",
        )

    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        unit_id=product_data.unit_id,
        available_quantity=product_data.available_quantity,
        min_stock=product_data.min_stock,
        max_stock=product_data.max_stock,
        is_locked=product_data.is_locked,
        status="active",
        created_by=current_user.id,
    )

    session.add(new_product)
    session.commit()
    session.refresh(new_product)

    return new_product


@router.patch(
    "/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK
)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    product = session.get(Product, product_id)
    if not product or product.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    if product.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El producto esta bloqueado y no puede ser modificado",
        )

    if product_data.name is not None and product_data.name != product.name:
        existing = session.exec(
            select(Product).where(
                Product.name == product_data.name,
                Product.id != product_id,
                Product.deleted_at == None,
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un producto con ese nombre",
            )

    if product_data.unit_id is not None:
        unit = session.get(Unit, product_data.unit_id)
        if not unit or unit.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unidad no encontrada",
            )

    update_fields = product_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(product, field, value)

    product.updated_at = datetime.now(timezone.utc)
    product.updated_by = current_user.id

    session.add(product)
    session.commit()
    session.refresh(product)

    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    product = session.get(Product, product_id)
    if not product or product.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    if product.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El producto esta bloqueado y no puede ser eliminado",
        )

    product.deleted_at = datetime.now(timezone.utc)
    product.deleted_by = current_user.id

    session.add(product)
    session.commit()

    return None


@router.patch(
    "/{product_id}/lock", response_model=ProductResponse, status_code=status.HTTP_200_OK
)
def toggle_product_lock(
    product_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    product = session.get(Product, product_id)
    if not product or product.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    product.is_locked = not product.is_locked
    product.updated_at = datetime.now(timezone.utc)
    product.updated_by = current_user.id

    session.add(product)
    session.commit()
    session.refresh(product)

    return product


# ── Carga masiva ────────────────────────────────────────────────────────────
BULK_PRODUCT_HEADERS = [
    "nombre",
    "descripcion",
    "unidad",
    "stock_disponible",
    "stock_min",
    "stock_max",
]
BULK_PRODUCT_EXAMPLES = [
    ["Pan frances", "Pan artesanal de 250g", "unidad", 120, 20, 300],
]


@router.post(
    "/bulk/import",
    response_model=BulkImportResult,
    status_code=status.HTTP_200_OK,
    summary="Cargar productos por archivo Excel/CSV (create o upsert)",
)
def bulk_import_products(
    mode: Literal["create", "upsert"] = Query(default="create"),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    rows = parse_spreadsheet(file)
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
        unidad_name = required(row, "unidad", "unidad")

        unit = units.get(unidad_name) or units_abbr.get(unidad_name)
        if unit is None:
            raise RowError(f"No existe la unidad '{row.get('unidad')}'.")

        existing = session.exec(
            select(Product).where(Product.name == nombre, Product.deleted_at == None)
        ).first()

        min_stock = safe_float(row.get("stock_min"), "stock_min")
        max_stock = safe_float(row.get("stock_max"), "stock_max")

        if mode == "upsert" and existing:
            if existing.is_locked:
                raise RowError(
                    f"El producto '{row.get('nombre')}' esta bloqueado y no puede ser modificado."
                )
            if descripcion is not None:
                existing.description = descripcion
            existing.min_stock = min_stock
            existing.max_stock = max_stock
            existing.updated_at = datetime.now(timezone.utc)
            existing.updated_by = current_user.id
            session.add(existing)
            return True

        if existing:
            raise RowError(f"Ya existe un producto con el nombre '{row.get('nombre')}'.")

        new_product = Product(
            name=nombre,
            description=descripcion,
            unit_id=unit.id,
            available_quantity=safe_float(row.get("stock_disponible"), "stock_disponible"),
            min_stock=min_stock,
            max_stock=max_stock,
            is_locked=False,
            status="active",
            created_by=current_user.id,
        )
        session.add(new_product)
        return False

    return run_bulk(session, rows, process_row)


@router.get(
    "/bulk/template",
    status_code=status.HTTP_200_OK,
    summary="Descargar plantilla de productos",
)
def bulk_products_template():
    return template_response(
        "plantilla_productos.xlsx", BULK_PRODUCT_HEADERS, BULK_PRODUCT_EXAMPLES
    )

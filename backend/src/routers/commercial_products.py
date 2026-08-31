from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlmodel import Session, select
from datetime import datetime
from zoneinfo import ZoneInfo

from src.database import get_session
from src.models.models import CommercialProduct, ProductCategory, Unit, Provider, User
from src.schemas.schemas import (
    CommercialProductCreate,
    CommercialProductUpdate,
    CommercialProductResponse,
    DeleteResponseCommercialProduct,
    BulkImportResult,
)
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

router = APIRouter(prefix="/commercial-products", tags=["CommercialProducts"])

BOGOTA_TZ = ZoneInfo("America/Bogota")


@router.get("/", response_model=list[CommercialProductResponse], status_code=status.HTTP_200_OK)
def get_all(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(CommercialProduct).where(CommercialProduct.deleted_at == None)).all()


@router.get("/{product_id}", response_model=CommercialProductResponse, status_code=status.HTTP_200_OK)
def get_one(product_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    product = session.get(CommercialProduct, product_id)
    if not product or product.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado.")
    return product


@router.post("/", response_model=CommercialProductResponse, status_code=status.HTTP_201_CREATED)
def create(data: CommercialProductCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    category = session.get(ProductCategory, data.category_id)
    if not category or category.status == "inactive":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La categoría con id '{data.category_id}' no existe.")

    unit = session.get(Unit, data.unit_id)
    if not unit or unit.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La unidad con id '{data.unit_id}' no existe.")

    if data.provider_id is not None:
        provider = session.get(Provider, data.provider_id)
        if not provider or provider.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El proveedor con id '{data.provider_id}' no existe.")

    existing = session.exec(
        select(CommercialProduct).where(
            CommercialProduct.name == data.name,
            CommercialProduct.deleted_at == None,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Ya existe un producto con el nombre '{data.name}'.")

    new_product = CommercialProduct(
        name=data.name,
        description=data.description,
        category_id=data.category_id,
        unit_id=data.unit_id,
        provider_id=data.provider_id,
        purchase_price=data.purchase_price,
        sale_price=data.sale_price,
        available_quantity=data.available_quantity,
        min_stock=data.min_stock,
        max_stock=data.max_stock,
        created_by=current_user.id,
    )
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    return new_product


@router.patch("/{product_id}", response_model=CommercialProductResponse, status_code=status.HTTP_200_OK)
def update(product_id: int, data: CommercialProductUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    product = session.get(CommercialProduct, product_id)
    if not product or product.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado.")

    if data.name and data.name != product.name:
        existing = session.exec(
            select(CommercialProduct).where(
                CommercialProduct.name == data.name,
                CommercialProduct.id != product_id,
                CommercialProduct.deleted_at == None,
            )
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Ya existe un producto con el nombre '{data.name}'.")

    if data.category_id is not None:
        category = session.get(ProductCategory, data.category_id)
        if not category or category.status == "inactive":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La categoría con id '{data.category_id}' no existe.")

    if data.unit_id is not None:
        unit = session.get(Unit, data.unit_id)
        if not unit or unit.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La unidad con id '{data.unit_id}' no existe.")

    if data.provider_id is not None:
        provider = session.get(Provider, data.provider_id)
        if not provider or provider.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El proveedor con id '{data.provider_id}' no existe.")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    product.updated_at = datetime.now(BOGOTA_TZ)
    product.updated_by = current_user.id
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete("/{product_id}", response_model=DeleteResponseCommercialProduct, status_code=status.HTTP_200_OK)
def delete(product_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    product = session.get(CommercialProduct, product_id)
    if not product or product.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado.")

    now = datetime.now(BOGOTA_TZ)
    product.deleted_at = now
    product.deleted_by = current_user.id
    product.status = "inactive"
    session.add(product)
    session.commit()

    return DeleteResponseCommercialProduct(
        message=f"Producto '{product.name}' eliminado correctamente.",
        deleted_at=now,
        deleted_by=current_user.id,
    )


# ── Carga masiva ────────────────────────────────────────────────────────────
BULK_COMMERCIAL_HEADERS = [
    "nombre",
    "descripcion",
    "categoria",
    "unidad",
    "proveedor",
    "precio_compra",
    "precio_venta",
    "stock_disponible",
    "stock_min",
    "stock_max",
]
BULK_COMMERCIAL_EXAMPLES = [
    ["Palitos de ajonjoli", "Empaque x12", "Snacks", "paquete", "Distribuidora ABC", 4200, 6500, 90, 20, 200],
]


@router.post(
    "/bulk/import",
    response_model=BulkImportResult,
    status_code=status.HTTP_200_OK,
    summary="Cargar productos comerciales por archivo Excel/CSV (create o upsert)",
)
def bulk_import_commercial(
    mode: Literal["create", "upsert"] = Query(default="create"),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    rows = parse_spreadsheet(file)
    categories = {
        name_key(c.name): c
        for c in session.exec(select(ProductCategory)).all()
        if c.status == "active" and c.deleted_at is None
    }
    units = {
        name_key(u.name): u
        for u in session.exec(select(Unit)).all()
        if u.deleted_at is None
    }
    units_abbr = {name_key(u.abbreviation): u for u in units.values()}
    providers = {
        name_key(p.company): p
        for p in session.exec(select(Provider)).all()
        if p.deleted_at is None and p.status == "active"
    }

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

        proveedor_value = row.get("proveedor")
        provider = None
        if proveedor_value is not None and str(proveedor_value).strip() != "":
            provider = providers.get(name_key(proveedor_value))
            if provider is None:
                raise RowError(f"No existe el proveedor '{proveedor_value}'.")

        precio_compra = safe_float(row.get("precio_compra"), "precio_compra")
        precio_venta = safe_float(row.get("precio_venta"), "precio_venta")
        min_stock = safe_float(row.get("stock_min"), "stock_min")
        max_stock = safe_float(row.get("stock_max"), "stock_max")

        existing = session.exec(
            select(CommercialProduct).where(
                CommercialProduct.name == nombre,
                CommercialProduct.deleted_at == None,
            )
        ).first()

        if mode == "upsert" and existing:
            if descripcion is not None:
                existing.description = descripcion
            existing.provider_id = provider.id if provider else None
            existing.purchase_price = precio_compra
            existing.sale_price = precio_venta
            existing.min_stock = min_stock
            existing.max_stock = max_stock
            existing.updated_at = datetime.now(BOGOTA_TZ)
            existing.updated_by = current_user.id
            session.add(existing)
            return True

        if existing:
            raise RowError(f"Ya existe un producto con el nombre '{row.get('nombre')}'.")

        new_product = CommercialProduct(
            name=nombre,
            description=descripcion,
            category_id=category.id,
            unit_id=unit.id,
            provider_id=provider.id if provider else None,
            purchase_price=precio_compra,
            sale_price=precio_venta,
            available_quantity=safe_float(row.get("stock_disponible"), "stock_disponible"),
            min_stock=min_stock,
            max_stock=max_stock,
            created_by=current_user.id,
        )
        session.add(new_product)
        return False

    return run_bulk(session, rows, process_row)


@router.get(
    "/bulk/template",
    status_code=status.HTTP_200_OK,
    summary="Descargar plantilla de productos comerciales",
)
def bulk_commercial_template():
    return template_response(
        "plantilla_productos_comerciales.xlsx",
        BULK_COMMERCIAL_HEADERS,
        BULK_COMMERCIAL_EXAMPLES,
    )
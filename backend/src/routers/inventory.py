from typing import Optional, List, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from io import BytesIO
from datetime import datetime, timezone
from openpyxl import Workbook

from src.database import get_session
from src.dependencies import require_module
from src.models.models import (
    Product,
    Supply,
    CommercialProduct,
    User,
)
from src.schemas.schemas import (
    InventoryItem,
    InventoryItemStatus,
    InventoryPage,
    InventorySummary,
)
from src.bulk.parser import (
    template_response,
)
from src.utils.excel import (
    apply_header_row, apply_data_row, auto_width, add_title_row,
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])


# ── Consulta consolidada ───────────────────────────────────────────────────
def _status_of(available: float, min_stock: float, max_stock: float) -> InventoryItemStatus:
    if available <= min_stock:
        return InventoryItemStatus.LOW
    if max_stock > 0 and available > max_stock:
        return InventoryItemStatus.OVER
    return InventoryItemStatus.NORMAL


def _build_rows(
    session: Session,
    item_type: Optional[str],
    stock_status: Optional[str],
    category_id: Optional[int],
    search: Optional[str],
    status_filter: Optional[str],
) -> List[InventoryItem]:
    rows: List[InventoryItem] = []

    def _matches(available: float, min_stock: float, max_stock: float) -> bool:
        if stock_status is None:
            return True
        return _status_of(available, min_stock, max_stock).value == stock_status

    if item_type in (None, "product"):
        q = select(Product).where(Product.deleted_at == None)
        if status_filter is not None:
            q = q.where(Product.status == status_filter)
        if search:
            q = q.where(Product.name.contains(search))
        for p in session.exec(q).all():
            if not _matches(p.available_quantity, p.min_stock, p.max_stock):
                continue
            rows.append(InventoryItem(
                id=p.id,
                item_type="product",
                name=p.name,
                description=p.description,
                category_name=None,
                unit_abbreviation=p.unit.abbreviation if p.unit else None,
                available_quantity=p.available_quantity,
                min_stock=p.min_stock,
                max_stock=p.max_stock,
                stock_status=_status_of(p.available_quantity, p.min_stock, p.max_stock),
                status=p.status,
            ))

    if item_type in (None, "supply"):
        q = select(Supply).where(Supply.deleted_at == None)
        if status_filter is not None:
            q = q.where(Supply.status == status_filter)
        if category_id is not None:
            q = q.where(Supply.category_id == category_id)
        if search:
            q = q.where(Supply.name.contains(search))
        for s in session.exec(q).all():
            if not _matches(s.available_quantity, s.min_stock, s.max_stock):
                continue
            rows.append(InventoryItem(
                id=s.id,
                item_type="supply",
                name=s.name,
                description=s.description,
                category_name=s.category.name if s.category else None,
                unit_abbreviation=s.unit.abbreviation if s.unit else None,
                available_quantity=s.available_quantity,
                min_stock=s.min_stock,
                max_stock=s.max_stock,
                stock_status=_status_of(s.available_quantity, s.min_stock, s.max_stock),
                status=s.status,
            ))

    if item_type in (None, "commercial"):
        q = select(CommercialProduct).where(CommercialProduct.deleted_at == None)
        if status_filter is not None:
            q = q.where(CommercialProduct.status == status_filter)
        if category_id is not None:
            q = q.where(CommercialProduct.category_id == category_id)
        if search:
            q = q.where(CommercialProduct.name.contains(search))
        for c in session.exec(q).all():
            if not _matches(c.available_quantity, c.min_stock, c.max_stock):
                continue
            rows.append(InventoryItem(
                id=c.id,
                item_type="commercial",
                name=c.name,
                description=c.description,
                category_name=c.category.name if c.category else None,
                unit_abbreviation=c.unit.abbreviation if c.unit else None,
                available_quantity=c.available_quantity,
                min_stock=c.min_stock,
                max_stock=c.max_stock,
                stock_status=_status_of(c.available_quantity, c.min_stock, c.max_stock),
                status=c.status,
            ))

    rows.sort(key=lambda r: r.name.lower())
    return rows


# ── Endpoints ──────────────────────────────────────────────────────────────
@router.get("/summary", response_model=InventoryPage, status_code=status.HTTP_200_OK)
def inventory_summary(
    item_type: Optional[Literal["supply", "product", "commercial"]] = Query(default=None),
    stock_status: Optional[Literal["bajo", "normal", "sobre"]] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
    search: Optional[str] = Query(default=None, max_length=150),
    status_filter: Optional[Literal["active", "inactive"]] = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(require_module("inventory")),
):
    if category_id is not None and item_type == "product":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El filtro de categoría solo aplica a insumos y productos comerciales.",
        )

    rows = _build_rows(session, item_type, stock_status, category_id, search, status_filter)
    total = len(rows)

    summary = InventorySummary(
        total_items=total,
        bajo_stock=sum(1 for r in rows if r.stock_status == InventoryItemStatus.LOW),
        sobre_stock=sum(1 for r in rows if r.stock_status == InventoryItemStatus.OVER),
    )

    start = (page - 1) * limit
    return InventoryPage(
        items=rows[start : start + limit],
        total=total,
        page=page,
        limit=limit,
        summary=summary,
    )


@router.get("/report", response_class=StreamingResponse)
def inventory_report(
    item_type: Optional[Literal["supply", "product", "commercial"]] = Query(default=None),
    stock_status: Optional[Literal["bajo", "normal", "sobre"]] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
    search: Optional[str] = Query(default=None, max_length=150),
    status_filter: Optional[Literal["active", "inactive"]] = Query(default=None, alias="status"),
    session: Session = Depends(get_session),
    current_user: User = Depends(require_module("inventory")),
):
    if category_id is not None and item_type == "product":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El filtro de categoría solo aplica a insumos y productos comerciales.",
        )

    rows = _build_rows(session, item_type, stock_status, category_id, search, status_filter)

    headers = ["Tipo", "Nombre", "Descripción", "Categoría", "Unidad",
               "Stock disponible", "Stock mínimo", "Stock máximo",
               "Estado de stock", "Estado"]
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario"
    ws.freeze_panes = "A3"

    apply_header_row(ws, headers)
    for i, r in enumerate(rows, start=2):
        apply_data_row(ws, i, [
            {"supply": "Insumo", "product": "Producto terminado", "commercial": "Comercial"}[r.item_type],
            r.name,
            r.description or "—",
            r.category_name or "—",
            r.unit_abbreviation or "—",
            r.available_quantity,
            r.min_stock,
            r.max_stock,
            {"bajo": "Bajo stock", "normal": "Normal", "sobre": "Sobre stock"}[r.stock_status.value],
            r.status,
        ])

    add_title_row(
        ws,
        f"Reporte de Inventario — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
        len(headers),
    )
    auto_width(ws, headers)

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = f"reporte_inventario_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ── Carga masiva de stock (entradas/descuentos) ─────────────────────────────
BULK_MOVEMENT_HEADERS = ["tipo", "nombre", "cantidad", "nota"]
BULK_MOVEMENT_EXAMPLES = [
    ["Insumo", "Harina de trigo", 50, "Compra semanal"],
    ["Producto", "Pan frances", 10, "Produccion extra"],
]


@router.get(
    "/bulk/template",
    status_code=status.HTTP_200_OK,
    summary="Descargar plantilla de movimientos de stock",
)
def bulk_movements_template():
    return template_response(
        "plantilla_movimientos_inventario.xlsx",
        BULK_MOVEMENT_HEADERS,
        BULK_MOVEMENT_EXAMPLES,
    )

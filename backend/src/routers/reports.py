from typing import Optional, Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlmodel import Session, select
from io import BytesIO
from datetime import datetime, timezone, date, time
from openpyxl import Workbook

from src.database import get_session
from src.dependencies import get_current_user
from src.models.models import (
    User, Role, SessionApp, Product, Supply,
    SupplyCategory, Unit, Recipe, ProductionOrder,
    ProductCategory, CommercialProduct, Provider,
)
from src.utils.excel import (
    apply_header_row, apply_data_row, auto_width, add_title_row,
    fmt_dt, fmt_bool,
)

router = APIRouter(prefix="/reports", tags=["Reports"])

ENTITY_MAP = {
    "users":             "Usuarios",
    "roles":             "Roles",
    "sessions":          "Sesiones",
    "products":          "Productos",
    "supplies":          "Insumos",
    "supply-categories": "Categorías de Insumos",
    "units":             "Unidades",
    "recipes":           "Recetas",
    "production":        "Órdenes de Producción",
    "providers":         "Proveedores",
    "product-categories": "Categorías de Productos",
    "commercial-products": "Productos Comerciales",
}

# Mapeo de cada entidad a su clase de modelo (para aplicar filtros genéricos)
ENTITY_MODEL = {
    "users":             User,
    "roles":             Role,
    "sessions":          SessionApp,
    "products":          Product,
    "supplies":          Supply,
    "supply-categories": SupplyCategory,
    "units":             Unit,
    "recipes":           Recipe,
    "production":        ProductionOrder,
    "providers":         Provider,
    "product-categories": ProductCategory,
    "commercial-products": CommercialProduct,
}


# ── Filtrado genérico ──────────────────────────────────────────────────────
def _apply_filters(query, model, filters: Dict[str, object]):
    """Aplica filtros genéricos a un select de SQLModel.

    Solo aplica un filtro si el modelo realmente posee el campo; si no,
    lo ignora silenciosamente. Sin filtros, devuelve el query sin cambios.
    Devuelve (query_filtrado, filtros_aplicados).
    """
    applied: Dict[str, object] = {}

    fecha_inicio = filters.get("fecha_inicio")
    fecha_fin = filters.get("fecha_fin")
    status = filters.get("status")
    search = filters.get("search")

    if fecha_inicio is not None and hasattr(model, "created_at"):
        query = query.where(model.created_at >= fecha_inicio)
        applied["fecha_inicio"] = fecha_inicio.isoformat()

    if fecha_fin is not None and hasattr(model, "created_at"):
        fin_dia = datetime.combine(fecha_fin, time.max)
        query = query.where(model.created_at <= fin_dia)
        applied["fecha_fin"] = fecha_fin.isoformat()

    if status is not None and hasattr(model, "status"):
        query = query.where(model.status == status)
        applied["status"] = status

    if search is not None and hasattr(model, "name"):
        query = query.where(model.name.contains(search))
        applied["search"] = search

    return query, applied


# ── Builders por entidad ───────────────────────────────────────────────────
# Cada builder escribe el worksheet y además devuelve (headers, data_rows, applied)
# donde data_rows es una lista de dicts serializables (para format=json).

def _build_users(ws, db: Session, filters: Dict[str, object]):
    headers = ["ID", "Nombre", "Apellido", "Correo", "Teléfono", "Rol",
               "Admin", "Estado", "Creado en"]
    query = select(User).where(User.deleted_at == None)
    query, applied = _apply_filters(query, User, filters)
    apply_header_row(ws, headers)
    users = db.exec(query).all()
    data = []
    for i, u in enumerate(users, start=2):
        role_name = u.role.name if u.role else "—"
        apply_data_row(ws, i, [
            u.id, u.first_name, u.last_name, u.email,
            u.phone or "—", role_name,
            fmt_bool(u.is_admin), u.status.value,
            fmt_dt(u.created_at),
        ])
        data.append({
            "id": u.id, "nombre": u.first_name, "apellido": u.last_name,
            "correo": u.email, "telefono": u.phone or None,
            "rol": role_name, "admin": u.is_admin, "estado": u.status.value,
            "creado_en": fmt_dt(u.created_at),
        })
    return headers, data, applied


def _build_roles(ws, db: Session, filters: Dict[str, object]):
    headers = ["ID", "Nombre", "Descripción", "Estado", "Creado en"]
    query = select(Role).where(Role.deleted_at == None)
    query, applied = _apply_filters(query, Role, filters)
    apply_header_row(ws, headers)
    roles = db.exec(query).all()
    data = []
    for i, r in enumerate(roles, start=2):
        apply_data_row(ws, i, [
            r.id, r.name, r.description,
            r.status.value, fmt_dt(r.created_at),
        ])
        data.append({
            "id": r.id, "nombre": r.name, "descripcion": r.description or None,
            "estado": r.status.value, "creado_en": fmt_dt(r.created_at),
        })
    return headers, data, applied


def _build_sessions(ws, db: Session, filters: Dict[str, object]):
    headers = ["ID", "Usuario", "Correo", "Activa", "Creada en", "Expira en"]
    query = select(SessionApp)
    query, applied = _apply_filters(query, SessionApp, filters)
    apply_header_row(ws, headers)
    sessions = db.exec(query).all()
    data = []
    for i, s in enumerate(sessions, start=2):
        user_name  = f"{s.user.first_name} {s.user.last_name}" if s.user else "—"
        user_email = s.user.email if s.user else "—"
        apply_data_row(ws, i, [
            s.id, user_name, user_email,
            fmt_bool(s.is_active),
            fmt_dt(s.created_at), fmt_dt(s.expires_at),
        ])
        data.append({
            "id": s.id, "usuario": user_name, "correo": user_email,
            "activa": s.is_active, "creada_en": fmt_dt(s.created_at),
            "expira_en": fmt_dt(s.expires_at),
        })
    return headers, data, applied


def _build_products(ws, db: Session, filters: Dict[str, object]):
    headers = ["ID", "Nombre", "Descripción", "Unidad", "Stock disponible",
               "Stock mínimo", "Stock máximo", "Bloqueado", "Estado", "Creado en"]
    query = select(Product).where(Product.deleted_at == None)
    query, applied = _apply_filters(query, Product, filters)
    apply_header_row(ws, headers)
    products = db.exec(query).all()
    data = []
    for i, p in enumerate(products, start=2):
        unit_name = p.unit.name if p.unit else "—"
        apply_data_row(ws, i, [
            p.id, p.name, p.description or "—",
            unit_name, p.available_quantity,
            p.min_stock, p.max_stock,
            fmt_bool(p.is_locked), p.status,
            fmt_dt(p.created_at),
        ])
        data.append({
            "id": p.id, "nombre": p.name, "descripcion": p.description or None,
            "unidad": unit_name, "stock_disponible": p.available_quantity,
            "stock_minimo": p.min_stock, "stock_maximo": p.max_stock,
            "bloqueado": p.is_locked, "estado": p.status,
            "creado_en": fmt_dt(p.created_at),
        })
    return headers, data, applied


def _build_supplies(ws, db: Session, filters: Dict[str, object]):
    headers = ["ID", "Nombre", "Descripción", "Categoría", "Unidad",
               "Stock disponible", "Stock mínimo", "Stock máximo",
               "Fecha vencimiento", "Estado", "Creado en"]
    query = select(Supply).where(Supply.deleted_at == None)
    query, applied = _apply_filters(query, Supply, filters)
    apply_header_row(ws, headers)
    supplies = db.exec(query).all()
    data = []
    for i, s in enumerate(supplies, start=2):
        cat_name  = s.category.name if s.category else "—"
        unit_name = s.unit.name if s.unit else "—"
        apply_data_row(ws, i, [
            s.id, s.name, s.description or "—",
            cat_name, unit_name,
            s.available_quantity, s.min_stock, s.max_stock,
            fmt_dt(s.expiration_date), s.status,
            fmt_dt(s.created_at),
        ])
        data.append({
            "id": s.id, "nombre": s.name, "descripcion": s.description or None,
            "categoria": cat_name, "unidad": unit_name,
            "stock_disponible": s.available_quantity, "stock_minimo": s.min_stock,
            "stock_maximo": s.max_stock, "fecha_vencimiento": fmt_dt(s.expiration_date),
            "estado": s.status, "creado_en": fmt_dt(s.created_at),
        })
    return headers, data, applied


def _build_supply_categories(ws, db: Session, filters: Dict[str, object]):
    headers = ["ID", "Nombre", "Descripción", "Estado", "Creado en"]
    query = select(SupplyCategory)
    query, applied = _apply_filters(query, SupplyCategory, filters)
    apply_header_row(ws, headers)
    categories = db.exec(query).all()
    data = []
    for i, c in enumerate(categories, start=2):
        apply_data_row(ws, i, [
            c.id, c.name, c.description or "—",
            c.status, fmt_dt(c.created_at),
        ])
        data.append({
            "id": c.id, "nombre": c.name, "descripcion": c.description or None,
            "estado": c.status, "creado_en": fmt_dt(c.created_at),
        })
    return headers, data, applied


def _build_units(ws, db: Session, filters: Dict[str, object]):
    headers = ["ID", "Nombre", "Abreviatura", "Descripción", "Cantidad", "Creado en"]
    query = select(Unit).where(Unit.deleted_at == None)
    query, applied = _apply_filters(query, Unit, filters)
    apply_header_row(ws, headers)
    units = db.exec(query).all()
    data = []
    for i, u in enumerate(units, start=2):
        apply_data_row(ws, i, [
            u.id, u.name, u.abbreviation,
            u.description or "—", u.quantity,
            fmt_dt(u.created_at),
        ])
        data.append({
            "id": u.id, "nombre": u.name, "abreviatura": u.abbreviation,
            "descripcion": u.description or None, "cantidad": u.quantity,
            "creado_en": fmt_dt(u.created_at),
        })
    return headers, data, applied


def _build_recipes(ws, db: Session, filters: Dict[str, object]):
    headers = ["ID", "Nombre", "Descripción", "Producto", "Rendimiento",
               "Unidad rendimiento", "Estado", "Creado en"]
    query = select(Recipe).where(Recipe.deleted_at == None)
    query, applied = _apply_filters(query, Recipe, filters)
    apply_header_row(ws, headers)
    recipes = db.exec(query).all()
    data = []
    for i, r in enumerate(recipes, start=2):
        product_name = r.product.name if r.product else "—"
        yield_unit   = r.yield_unit.name if r.yield_unit else "—"
        apply_data_row(ws, i, [
            r.id, r.name, r.description or "—",
            product_name, r.yield_quantity,
            yield_unit, r.status.value,
            fmt_dt(r.created_at),
        ])
        data.append({
            "id": r.id, "nombre": r.name, "descripcion": r.description or None,
            "producto": product_name, "rendimiento": r.yield_quantity,
            "unidad_rendimiento": yield_unit, "estado": r.status.value,
            "creado_en": fmt_dt(r.created_at),
        })
    return headers, data, applied


def _build_production(ws, db: Session, filters: Dict[str, object]):
    headers = ["ID", "Receta", "Multiplicador", "Rendimiento total",
               "Estado", "Programado para", "Completado en",
               "Notas", "Creado en"]
    query = select(ProductionOrder).where(ProductionOrder.deleted_at == None)
    query, applied = _apply_filters(query, ProductionOrder, filters)
    apply_header_row(ws, headers)
    orders = db.exec(query).all()
    data = []
    for i, o in enumerate(orders, start=2):
        recipe_name = o.recipe.name if o.recipe else "—"
        apply_data_row(ws, i, [
            o.id, recipe_name,
            o.quantity_multiplier, o.total_yield,
            o.status.value,
            fmt_dt(o.scheduled_at), fmt_dt(o.completed_at),
            o.notes or "—", fmt_dt(o.created_at),
        ])
        data.append({
            "id": o.id, "receta": recipe_name,
            "multiplicador": o.quantity_multiplier, "rendimiento_total": o.total_yield,
            "estado": o.status.value,
            "programado_para": fmt_dt(o.scheduled_at),
            "completado_en": fmt_dt(o.completed_at),
            "notas": o.notes or None, "creado_en": fmt_dt(o.created_at),
        })
    return headers, data, applied


def _build_providers(ws, db: Session, filters: Dict[str, object]):
    headers = ["ID", "Empresa", "NIT", "Correo", "Estado", "Creado en"]
    query = select(Provider).where(Provider.deleted_at == None)
    query, applied = _apply_filters(query, Provider, filters)
    apply_header_row(ws, headers)
    providers = db.exec(query).all()
    data = []
    for i, p in enumerate(providers, start=2):
        apply_data_row(ws, i, [
            p.id, p.company, p.nit, p.email,
            p.status.value, fmt_dt(p.created_at),
        ])
        data.append({
            "id": p.id, "empresa": p.company, "nit": p.nit,
            "correo": p.email, "estado": p.status.value,
            "creado_en": fmt_dt(p.created_at),
        })
    return headers, data, applied


def _build_product_categories(ws, db: Session, filters: Dict[str, object]):
    headers = ["ID", "Nombre", "Descripción", "Estado", "Creado en"]
    query = select(ProductCategory).where(ProductCategory.deleted_at == None)
    query, applied = _apply_filters(query, ProductCategory, filters)
    apply_header_row(ws, headers)
    categories = db.exec(query).all()
    data = []
    for i, c in enumerate(categories, start=2):
        apply_data_row(ws, i, [
            c.id, c.name, c.description or "—",
            c.status, fmt_dt(c.created_at),
        ])
        data.append({
            "id": c.id, "nombre": c.name, "descripcion": c.description or None,
            "estado": c.status, "creado_en": fmt_dt(c.created_at),
        })
    return headers, data, applied


def _build_commercial_products(ws, db: Session, filters: Dict[str, object]):
    headers = ["ID", "Nombre", "Categoría", "Unidad", "Proveedor",
               "P. compra", "P. venta", "Stock disponible",
               "Stock mínimo", "Stock máximo", "Estado", "Creado en"]
    query = select(CommercialProduct).where(CommercialProduct.deleted_at == None)
    query, applied = _apply_filters(query, CommercialProduct, filters)
    apply_header_row(ws, headers)
    products = db.exec(query).all()
    data = []
    for i, p in enumerate(products, start=2):
        cat_name     = p.category.name if p.category else "—"
        unit_abbr    = p.unit.abbreviation if p.unit else "—"
        provider_name = p.provider.company if p.provider else "—"
        apply_data_row(ws, i, [
            p.id, p.name, cat_name, unit_abbr, provider_name,
            p.purchase_price, p.sale_price, p.available_quantity,
            p.min_stock, p.max_stock, p.status,
            fmt_dt(p.created_at),
        ])
        data.append({
            "id": p.id, "nombre": p.name, "categoria": cat_name,
            "unidad": unit_abbr, "proveedor": provider_name,
            "precio_compra": p.purchase_price, "precio_venta": p.sale_price,
            "stock_disponible": p.available_quantity,
            "stock_minimo": p.min_stock, "stock_maximo": p.max_stock,
            "estado": p.status, "creado_en": fmt_dt(p.created_at),
        })
    return headers, data, applied


BUILDERS = {
    "users":             _build_users,
    "roles":             _build_roles,
    "sessions":          _build_sessions,
    "products":          _build_products,
    "supplies":          _build_supplies,
    "supply-categories": _build_supply_categories,
    "units":             _build_units,
    "recipes":           _build_recipes,
    "production":        _build_production,
    "providers":         _build_providers,
    "product-categories": _build_product_categories,
    "commercial-products": _build_commercial_products,
}


# ── Endpoint ───────────────────────────────────────────────────────────────
@router.get(
    "/{entity}",
    summary="Generar reporte por entidad (Excel o JSON)",
)
def generate_report(
    entity: str,
    fecha_inicio: Optional[date] = Query(default=None),
    fecha_fin: Optional[date] = Query(default=None),
    status: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None, max_length=150),
    format: str = Query(default="xlsx", pattern="^(xlsx|json)$"),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if entity not in BUILDERS:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Entidad '{entity}' no soportada. Opciones: {list(BUILDERS.keys())}",
        )

    filters: Dict[str, object] = {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "status": status,
        "search": search,
    }

    # ── Respuesta JSON ──────────────────────────────────────────────────────
    if format == "json":
        # En JSON no hace falta crear un workbook; los builders aceptan ws=None.
        headers, data, applied = BUILDERS[entity](None, db, filters)
        return JSONResponse({
            "entity": entity,
            "total": len(data),
            "filters_applied": applied,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "data": data,
        })

    # ── Respuesta Excel (por defecto) ───────────────────────────────────────
    wb = Workbook()
    ws = wb.active
    ws.title = ENTITY_MAP.get(entity, entity.capitalize())
    ws.freeze_panes = "A3"

    headers, _, _ = BUILDERS[entity](ws, db, filters)

    col_count = len(headers)
    add_title_row(
        ws,
        f"Reporte de {ENTITY_MAP.get(entity, entity)} — "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
        col_count,
    )
    auto_width(ws, headers)

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = f"reporte_{entity}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

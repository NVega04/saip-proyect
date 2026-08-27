from datetime import datetime, timedelta
from typing import List, Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session, select, func

from src.database import get_session
from src.models.models import (
    Supply,
    Unit,
    ProductionOrder,
    ProductionOrderSnapshot,
    ProductionOrderStatus,
    Product,
    CommercialProduct,
    ProductCategory,
    Recipe,
    Sale,
    SaleItem,
    SaleStatus,
    User,
)
from src.schemas.schemas import (
    DashboardStatsResponse,
    DashboardKpis,
    ConsumptionPoint,
    StockLevelPoint,
    LowStockSupplyItem,
    ExpiringSupplyItem,
    SalesKpis,
    DailySalesPoint,
    TopSaleItem,
    SalesSection,
    ProductionByStatusPoint,
    DailyProductionPoint,
    TopRecipePoint,
    ProductionSection,
    ProductsKpis,
    ProductStockPoint,
    LowStockProduct,
    ProductProductionPoint,
    CommercialStockPoint,
    CategoryCountPoint,
    StockHealthPoint,
    ProductsSection,
)
from src.dependencies import get_current_user

router = APIRouter(prefix="/stats", tags=["Stats"])

BOGOTA_TZ = ZoneInfo("America/Bogota")
EXPIRATION_WINDOW_DAYS = 7
MAX_STOCK_LEVEL_POINTS = 10


def _aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=BOGOTA_TZ)
    return dt


@router.get(
    "/dashboard",
    response_model=DashboardStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Estadísticas agregadas de insumos para el dashboard",
)
def get_dashboard(
    days: int = Query(default=30, ge=1, le=365),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now(BOGOTA_TZ)

    # ── 1. Insumos activos ────────────────────────────────────────────────────
    supplies = session.exec(
        select(Supply).where(Supply.deleted_at == None, Supply.status == "active")
    ).all()

    low_stock_supplies = [
        s for s in supplies if s.available_quantity <= s.min_stock
    ]
    low_stock_supplies.sort(key=lambda s: s.available_quantity - s.min_stock)

    expiration_limit = now + timedelta(days=EXPIRATION_WINDOW_DAYS)
    expired_supplies = [
        s
        for s in supplies
        if s.expiration_date is not None and _aware(s.expiration_date) < now
    ]
    expired_supplies.sort(key=lambda s: s.expiration_date)
    expiring_soon_supplies = [
        s
        for s in supplies
        if s.expiration_date is not None
        and now <= _aware(s.expiration_date) <= expiration_limit
    ]
    expiring_soon_supplies.sort(key=lambda s: s.expiration_date)

    # ── 2. Consumo por día (snapshots de órdenes completadas) ────────────────
    period_start = now - timedelta(days=days)
    rows = session.exec(
        select(
            func.date(ProductionOrder.completed_at),
            func.coalesce(func.sum(ProductionOrderSnapshot.quantity_used), 0.0),
        )
        .join(
            ProductionOrder,
            ProductionOrder.id == ProductionOrderSnapshot.production_order_id,
        )
        .where(
            ProductionOrder.deleted_at == None,
            ProductionOrder.status == ProductionOrderStatus.COMPLETED,
            ProductionOrder.completed_at >= period_start,
        )
        .group_by(func.date(ProductionOrder.completed_at))
        .order_by(func.date(ProductionOrder.completed_at))
    ).all()

    consumption_by_date: dict[str, float] = {
        str(row[0]): float(row[1]) for row in rows
    }

    def _date_keys() -> List[str]:
        keys: List[str] = []
        cursor = (now - timedelta(days=days)).date()
        end = now.date()
        while cursor <= end:
            keys.append(cursor.isoformat())
            cursor += timedelta(days=1)
        return keys

    date_keys = _date_keys()

    tendencia: List[ConsumptionPoint] = [
        ConsumptionPoint(fecha=k, cantidad=consumption_by_date.get(k, 0.0))
        for k in date_keys
    ]

    # ── 2b. Consumo por unidad de medida ─────────────────────────────────────
    unit_rows = session.exec(
        select(
            Unit.abbreviation,
            func.coalesce(func.sum(ProductionOrderSnapshot.quantity_used), 0.0),
        )
        .join(
            ProductionOrder,
            ProductionOrder.id == ProductionOrderSnapshot.production_order_id,
        )
        .join(
            Unit,
            Unit.id == ProductionOrderSnapshot.unit_id,
        )
        .where(
            ProductionOrder.deleted_at == None,
            ProductionOrder.status == ProductionOrderStatus.COMPLETED,
            ProductionOrder.completed_at >= period_start,
        )
        .group_by(Unit.abbreviation)
    ).all()

    consumo_por_unidad: dict[str, float] = {
        str(row[0] or "ud"): float(row[1]) for row in unit_rows if float(row[1]) > 0
    }

    # ── 3. Niveles de stock (insumos más críticos primero) ───────────────────
    most_critical = low_stock_supplies + [
        s for s in supplies if s not in low_stock_supplies
    ]
    niveles = [
        StockLevelPoint(
            name=s.name,
            disponible=s.available_quantity,
            minimo=s.min_stock,
        )
        for s in most_critical[:MAX_STOCK_LEVEL_POINTS]
    ]

    # ── 4. KPIs y listas detalladas ──────────────────────────────────────────
    kpis = DashboardKpis(
        insumos_activos=len(supplies),
        stock_bajo_count=len(low_stock_supplies),
        vencidos_count=len(expired_supplies),
        por_vencer_count=len(expiring_soon_supplies),
        consumo_periodo=float(sum(p.cantidad for p in tendencia)),
        consumo_por_unidad=consumo_por_unidad,
    )

    stock_bajo: List[LowStockSupplyItem] = []
    for s in low_stock_supplies:
        category_name: Optional[str] = None
        unit_abbr: Optional[str] = None
        try:
            category_name = s.category.name if s.category else None
        except Exception:
            category_name = None
        try:
            unit_abbr = s.unit.abbreviation if s.unit else None
        except Exception:
            unit_abbr = None
        stock_bajo.append(
            LowStockSupplyItem(
                id=s.id,
                name=s.name,
                category=category_name,
                unit=unit_abbr,
                available_quantity=s.available_quantity,
                min_stock=s.min_stock,
            )
        )

    def _to_expiring_item(s: Supply) -> ExpiringSupplyItem:
        exp_aware = _aware(s.expiration_date) if s.expiration_date else now
        return ExpiringSupplyItem(
            id=s.id,
            name=s.name,
            expiration_date=exp_aware,
            days_remaining=(exp_aware - now).days,
            available_quantity=s.available_quantity,
        )

    vencidos: List[ExpiringSupplyItem] = [
        _to_expiring_item(s) for s in expired_supplies
    ]
    por_vencer: List[ExpiringSupplyItem] = [
        _to_expiring_item(s) for s in expiring_soon_supplies
    ]

    # ── 5. Ventas ────────────────────────────────────────────────────────────
    sale_period_filter = Sale.sale_date >= period_start
    completed_filter = Sale.status == SaleStatus.COMPLETED
    deleted_sale_filter = Sale.deleted_at == None

    sales_count_rows = session.exec(
        select(func.date(Sale.sale_date), func.count(Sale.id))
        .where(deleted_sale_filter, completed_filter, sale_period_filter)
        .group_by(func.date(Sale.sale_date))
        .order_by(func.date(Sale.sale_date))
    ).all()

    sales_qty_rows = session.exec(
        select(func.date(Sale.sale_date), func.coalesce(func.sum(SaleItem.quantity), 0.0))
        .select_from(Sale)
        .join(SaleItem, SaleItem.sale_id == Sale.id)
        .where(deleted_sale_filter, completed_filter, sale_period_filter)
        .group_by(func.date(Sale.sale_date))
        .order_by(func.date(Sale.sale_date))
    ).all()

    sales_count_map: dict[str, int] = {str(r[0]): int(r[1]) for r in sales_count_rows}
    sales_qty_map: dict[str, float] = {str(r[0]): float(r[1]) for r in sales_qty_rows}

    tendencia_ventas: List[DailySalesPoint] = [
        DailySalesPoint(
            fecha=k,
            num_ventas=sales_count_map.get(k, 0),
            cantidad=sales_qty_map.get(k, 0.0),
        )
        for k in date_keys
    ]

    today_key = now.date().isoformat()
    ventas_hoy = sales_count_map.get(today_key, 0)
    unidades_hoy = sales_qty_map.get(today_key, 0.0)
    unidades_periodo = sum(p.cantidad for p in tendencia_ventas)

    anuladas_periodo = session.exec(
        select(func.count(Sale.id))
        .where(
            deleted_sale_filter,
            Sale.status == SaleStatus.ANNULLED,
            sale_period_filter,
        )
    ).one()

    top_item_rows = session.exec(
        select(SaleItem.item_name, func.coalesce(func.sum(SaleItem.quantity), 0.0))
        .select_from(SaleItem)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .where(deleted_sale_filter, completed_filter, sale_period_filter)
        .group_by(SaleItem.item_name)
        .order_by(func.sum(SaleItem.quantity).desc())
        .limit(8)
    ).all()

    ventas_section = SalesSection(
        kpis=SalesKpis(
            ventas_hoy=ventas_hoy,
            unidades_hoy=unidades_hoy,
            unidades_periodo=unidades_periodo,
            anuladas_periodo=int(anuladas_periodo or 0),
        ),
        tendencia=tendencia_ventas,
        top_items=[TopSaleItem(name=str(r[0]), cantidad=float(r[1])) for r in top_item_rows],
    )

    # ── 6. Producción ────────────────────────────────────────────────────────
    status_rows = session.exec(
        select(ProductionOrder.status, func.count(ProductionOrder.id))
        .where(ProductionOrder.deleted_at == None)
        .group_by(ProductionOrder.status)
    ).all()

    status_map: dict[str, int] = {}
    for s_val, count in status_rows:
        status_map[str(s_val.value) if hasattr(s_val, "value") else str(s_val)] = int(count)

    por_estado = [
        ProductionByStatusPoint(estado=s, total=status_map.get(s, 0))
        for s in ["pending", "in_progress", "completed", "cancelled"]
    ]

    yield_rows = session.exec(
        select(
            func.date(ProductionOrder.completed_at),
            func.coalesce(func.sum(ProductionOrder.total_yield), 0.0),
        )
        .where(
            ProductionOrder.deleted_at == None,
            ProductionOrder.status == ProductionOrderStatus.COMPLETED,
            ProductionOrder.completed_at >= period_start,
            ProductionOrder.completed_at != None,
        )
        .group_by(func.date(ProductionOrder.completed_at))
        .order_by(func.date(ProductionOrder.completed_at))
    ).all()

    yield_map: dict[str, float] = {str(r[0]): float(r[1]) for r in yield_rows}

    rendimiento_diario: List[DailyProductionPoint] = [
        DailyProductionPoint(fecha=k, unidades=yield_map.get(k, 0.0))
        for k in date_keys
    ]

    recipe_rows = session.exec(
        select(
            Recipe.name,
            func.count(ProductionOrder.id),
            func.coalesce(func.sum(ProductionOrder.total_yield), 0.0),
        )
        .select_from(ProductionOrder)
        .join(Recipe, Recipe.id == ProductionOrder.recipe_id)
        .where(
            ProductionOrder.deleted_at == None,
            ProductionOrder.status == ProductionOrderStatus.COMPLETED,
            ProductionOrder.completed_at >= period_start,
        )
        .group_by(Recipe.name)
        .order_by(func.count(ProductionOrder.id).desc())
        .limit(5)
    ).all()

    produccion_section = ProductionSection(
        por_estado=por_estado,
        rendimiento_diario=rendimiento_diario,
        top_recetas=[
            TopRecipePoint(nombre=str(r[0]), veces=int(r[1]), unidades=float(r[2]))
            for r in recipe_rows
        ],
    )

    # ── 7. Productos terminados ──────────────────────────────────────────────
    products = session.exec(
        select(Product).where(Product.deleted_at == None, Product.status == "active")
    ).all()

    products_low_stock = [
        p for p in products if p.available_quantity <= p.min_stock
    ]
    products_low_stock.sort(key=lambda p: p.available_quantity - p.min_stock)

    products_stock = [
        ProductStockPoint(
            name=p.name,
            disponible=p.available_quantity,
            minimo=p.min_stock,
            maximo=p.max_stock,
        )
        for p in sorted(
            products_low_stock + [p for p in products if p not in products_low_stock],
            key=lambda p: p.available_quantity - p.min_stock,
        )[:MAX_STOCK_LEVEL_POINTS]
    ]

    produccion_por_producto_rows = session.exec(
        select(
            Recipe.name,
            func.count(ProductionOrder.id),
            func.coalesce(func.sum(ProductionOrder.total_yield), 0.0),
        )
        .select_from(ProductionOrder)
        .join(Recipe, Recipe.id == ProductionOrder.recipe_id)
        .join(Product, Product.id == Recipe.product_id)
        .where(
            ProductionOrder.deleted_at == None,
            ProductionOrder.status == ProductionOrderStatus.COMPLETED,
            ProductionOrder.completed_at >= period_start,
            Product.deleted_at == None,
        )
        .group_by(Recipe.name)
        .order_by(func.count(ProductionOrder.id).desc())
        .limit(10)
    ).all()

    produccion_por_producto = [
        ProductProductionPoint(
            nombre=str(r[0]), total=int(r[1]), unidades=float(r[2])
        )
        for r in produccion_por_producto_rows
    ]

    def _to_low_product(p: Product) -> LowStockProduct:
        unit_name: Optional[str] = None
        try:
            unit_name = p.unit.abbreviation if p.unit else None
        except Exception:
            unit_name = None
        return LowStockProduct(
            id=p.id,
            name=p.name,
            unit=unit_name,
            available_quantity=p.available_quantity,
            min_stock=p.min_stock,
            max_stock=p.max_stock,
        )

    productos_stock_bajo: List[LowStockProduct] = [
        _to_low_product(p) for p in products_low_stock
    ]

    # ── 8. Productos comerciales ─────────────────────────────────────────────
    commercials = session.exec(
        select(CommercialProduct).where(
            CommercialProduct.deleted_at == None, CommercialProduct.status == "active"
        )
    ).all()

    commercials_low_stock = [
        c for c in commercials if c.available_quantity <= c.min_stock
    ]
    commercials_low_stock.sort(key=lambda c: c.available_quantity - c.min_stock)

    commercials_stock = [
        CommercialStockPoint(
            name=c.name,
            disponible=c.available_quantity,
            minimo=c.min_stock,
        )
        for c in sorted(
            commercials_low_stock
            + [c for c in commercials if c not in commercials_low_stock],
            key=lambda c: c.available_quantity - c.min_stock,
        )[:MAX_STOCK_LEVEL_POINTS]
    ]

    def _to_low_commercial(c: CommercialProduct) -> LowStockProduct:
        unit_name: Optional[str] = None
        try:
            unit_name = c.unit.abbreviation if c.unit else None
        except Exception:
            unit_name = None
        return LowStockProduct(
            id=c.id,
            name=c.name,
            unit=unit_name,
            available_quantity=c.available_quantity,
            min_stock=c.min_stock,
            max_stock=c.max_stock,
        )

    comerciales_stock_bajo: List[LowStockProduct] = [
        _to_low_commercial(c) for c in commercials_low_stock
    ]

    cat_rows = session.exec(
        select(ProductCategory.name, func.count(CommercialProduct.id))
        .select_from(CommercialProduct)
        .join(ProductCategory, ProductCategory.id == CommercialProduct.category_id)
        .where(
            CommercialProduct.deleted_at == None,
            CommercialProduct.status == "active",
        )
        .group_by(ProductCategory.name)
        .order_by(func.count(CommercialProduct.id).desc())
    ).all()

    por_categoria = [
        CategoryCountPoint(name=str(r[0]), total=int(r[1])) for r in cat_rows
    ]

    healthy = sum(1 for c in commercials if c.available_quantity > c.min_stock)
    low = len(commercials_low_stock)
    out = sum(1 for c in commercials if c.available_quantity <= 0)

    stock_saludable = [
        StockHealthPoint(estado="OK", total=healthy),
        StockHealthPoint(estado="Bajo mínimo", total=low),
        StockHealthPoint(estado="Sin stock", total=out),
    ]

    products_section = ProductsSection(
        kpis=ProductsKpis(
            productos_activos=len(products),
            productos_stock_bajo=len(products_low_stock),
            comerciales_activos=len(commercials),
            comerciales_stock_bajo=len(commercials_low_stock),
        ),
        productos_stock=products_stock,
        productos_stock_bajo=productos_stock_bajo,
        produccion_por_producto=produccion_por_producto,
        comerciales_stock=commercials_stock,
        comerciales_stock_bajo=comerciales_stock_bajo,
        por_categoria=por_categoria,
        stock_saludable=stock_saludable,
    )

    return DashboardStatsResponse(
        kpis=kpis,
        consumo_tendencia=tendencia,
        niveles_stock=niveles,
        stock_bajo=stock_bajo,
        vencidos=vencidos,
        por_vencer=por_vencer,
        ventas=ventas_section,
        produccion=produccion_section,
        productos=products_section,
    )

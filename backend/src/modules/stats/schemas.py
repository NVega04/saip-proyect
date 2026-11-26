from datetime import datetime
from typing import List

from pydantic import BaseModel


class DashboardKpis(BaseModel):
    insumos_activos: int
    stock_bajo_count: int
    vencidos_count: int
    por_vencer_count: int
    consumo_periodo: float
    consumo_por_unidad: dict[str, float] = {}


class ConsumptionPoint(BaseModel):
    fecha: str
    cantidad: float


class StockLevelPoint(BaseModel):
    name: str
    disponible: float
    minimo: float


class LowStockSupplyItem(BaseModel):
    id: int
    name: str
    category: str | None = None
    unit: str | None = None
    available_quantity: float
    min_stock: float


class ExpiringSupplyItem(BaseModel):
    id: int
    name: str
    expiration_date: datetime
    days_remaining: int
    available_quantity: float


class SalesKpis(BaseModel):
    ventas_hoy: int
    unidades_hoy: float
    unidades_periodo: float
    anuladas_periodo: int


class DailySalesPoint(BaseModel):
    fecha: str
    num_ventas: int
    cantidad: float


class TopSaleItem(BaseModel):
    name: str
    cantidad: float


class ProductionByStatusPoint(BaseModel):
    estado: str
    total: int


class DailyProductionPoint(BaseModel):
    fecha: str
    unidades: float


class TopRecipePoint(BaseModel):
    nombre: str
    veces: int
    unidades: float


class SalesSection(BaseModel):
    kpis: SalesKpis
    tendencia: List[DailySalesPoint]
    top_items: List[TopSaleItem]


class ProductionSection(BaseModel):
    por_estado: List[ProductionByStatusPoint]
    rendimiento_diario: List[DailyProductionPoint]
    top_recetas: List[TopRecipePoint]


class ProductsKpis(BaseModel):
    productos_activos: int
    productos_stock_bajo: int
    comerciales_activos: int
    comerciales_stock_bajo: int


class ProductStockPoint(BaseModel):
    name: str
    disponible: float
    minimo: float
    maximo: float


class LowStockProduct(BaseModel):
    id: int
    name: str
    unit: str | None = None
    available_quantity: float
    min_stock: float
    max_stock: float


class ProductProductionPoint(BaseModel):
    nombre: str
    total: int
    unidades: float


class CommercialStockPoint(BaseModel):
    name: str
    disponible: float
    minimo: float


class CategoryCountPoint(BaseModel):
    name: str
    total: int


class StockHealthPoint(BaseModel):
    estado: str
    total: int


class ProductsSection(BaseModel):
    kpis: ProductsKpis
    productos_stock: List[ProductStockPoint]
    productos_stock_bajo: List[LowStockProduct]
    produccion_por_producto: List[ProductProductionPoint]
    comerciales_stock: List[CommercialStockPoint]
    comerciales_stock_bajo: List[LowStockProduct]
    por_categoria: List[CategoryCountPoint]
    stock_saludable: List[StockHealthPoint]


class DashboardStatsResponse(BaseModel):
    kpis: DashboardKpis
    consumo_tendencia: List[ConsumptionPoint]
    niveles_stock: List[StockLevelPoint]
    stock_bajo: List[LowStockSupplyItem]
    vencidos: List[ExpiringSupplyItem]
    por_vencer: List[ExpiringSupplyItem]
    ventas: SalesSection
    produccion: ProductionSection
    productos: ProductsSection

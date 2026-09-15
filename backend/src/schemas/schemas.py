from datetime import datetime
from enum import Enum
from typing import ClassVar

from pydantic import BaseModel, EmailStr, Field, field_validator
from src.models.models import (
    ItemType,
    ProductionOrderStatus,
    ProductStatus,
    ProviderStatus,
    RecipeStatus,
    RoleStatus,
    SaleStatus,
    UserStatus,
)


class UppercaseMixin:
    EXCLUDE_FIELDS: ClassVar[set[str]] = {
        "email",
        "description",
        "password",
        "token",
        "new_password",
        "current_password",
        "notas",
        "observaciones",
        "status",
    }

    @field_validator("*", mode="before")
    @classmethod
    def uppercase_strings(cls, v, info):
        if info.field_name in cls.EXCLUDE_FIELDS:
            return v
        if isinstance(v, str) and v.strip():
            return v.upper().strip()
        return v


## Esquemas relacionados a Usuarios.
class UserCreate(UppercaseMixin, BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    role_id: int
    is_admin: bool = False


class RoleBasic(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str | None
    role_id: int
    role: RoleBasic
    is_admin: bool
    status: UserStatus
    created_at: datetime
    accepted_terms: bool
    accepted_terms_at: datetime | None

    class Config:
        from_attributes = True


class DeleteResponseUser(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int


class UserUpdate(UppercaseMixin, BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    role_id: int | None = None
    is_admin: bool | None = None
    status: UserStatus | None = None


class UserUpdateResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str | None
    role_id: int
    role: RoleBasic
    is_admin: bool
    status: UserStatus
    created_at: datetime
    updated_at: datetime | None
    updated_by: int | None

    class Config:
        from_attributes = True


## Esquemas relacionados a Roles.
class RoleCreate(UppercaseMixin, BaseModel):
    name: str
    description: str


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


## Esquemas relacionados a sesiones en el sistema.
class RoleUpdate(UppercaseMixin, BaseModel):
    name: str | None = None
    description: str | None = None


class RolePublic(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    status: RoleStatus
    updated_at: datetime | None = None
    updated_by: int | None = None
    deleted_at: datetime | None = None
    deleted_by: int | None = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    accepted_terms: bool = False


class LoginResponse(BaseModel):
    session_token: str
    expires_at: datetime
    user: UserResponse
    terms_required: bool = False


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


## Esquemas relacionados a Módulos
class ModuleResponse(BaseModel):
    id: int
    token: str
    name: str
    label: str

    class Config:
        from_attributes = True


## Esquemas relacionados a RoleModules
class RoleModuleAssign(BaseModel):
    module_ids: list[int]


class RoleModuleResponse(BaseModel):
    id: int
    token: str
    role_id: int
    module_id: int
    module: ModuleResponse  # ← agregar relación

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


## Esquemas relacionados a Units (Unidades de medida)
class UnitCreate(UppercaseMixin, BaseModel):
    name: str
    abbreviation: str
    description: str | None = None
    quantity: float


class UnitUpdate(UppercaseMixin, BaseModel):
    name: str | None = None
    abbreviation: str | None = None
    description: str | None = None
    quantity: float | None = None


class UnitResponse(BaseModel):
    id: int
    token: str
    name: str
    abbreviation: str
    description: str | None
    quantity: float
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None

    class Config:
        from_attributes = True


## Esquemas relacionados a Products (Productos/Ingredientes)
class UnitBasic(BaseModel):
    id: int
    name: str
    abbreviation: str

    class Config:
        from_attributes = True


class ProductCreate(UppercaseMixin, BaseModel):
    name: str
    description: str | None = None
    unit_id: int
    available_quantity: float = 0
    min_stock: float = 0
    max_stock: float = 0
    is_locked: bool = False


class ProductUpdate(UppercaseMixin, BaseModel):
    name: str | None = None
    description: str | None = None
    unit_id: int | None = None
    available_quantity: float | None = None
    min_stock: float | None = None
    max_stock: float | None = None
    is_locked: bool | None = None


class ProductResponse(BaseModel):
    id: int
    token: str
    name: str
    description: str | None
    unit_id: int
    unit: UnitBasic
    available_quantity: float
    min_stock: float
    max_stock: float
    is_locked: bool
    status: ProductStatus
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None

    class Config:
        from_attributes = True

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v):
        if isinstance(v, str):
            return ProductStatus(v.lower())
        return v


## Esquemas relacionados a SupplyCategory
class SupplyBasic(BaseModel):
    id: int
    token: str
    name: str
    status: str

    class Config:
        from_attributes = True


class SupplyCategoryCreate(UppercaseMixin, BaseModel):
    name: str
    description: str | None = None


class SupplyCategoryUpdate(UppercaseMixin, BaseModel):
    name: str | None = None
    description: str | None = None


class SupplyCategoryResponse(BaseModel):
    id: int
    token: str
    name: str
    description: str | None
    status: str
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None
    supplies: list[SupplyBasic]

    class Config:
        from_attributes = True


class DeleteResponseSupplyCategory(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int


## Esquemas relacionados a Supply (Insumos)
class SupplyCategoryBasic(BaseModel):
    id: int
    token: str
    name: str

    class Config:
        from_attributes = True


class SupplyCreate(UppercaseMixin, BaseModel):
    name: str
    description: str | None = None
    category_id: int
    unit_id: int
    available_quantity: float = 0
    min_stock: float = 0
    max_stock: float = 0
    supplier_id: int | None = None
    expiration_date: datetime | None = None


class SupplyUpdate(UppercaseMixin, BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    unit_id: int | None = None
    available_quantity: float | None = None
    min_stock: float | None = None
    max_stock: float | None = None
    supplier_id: int | None = None
    expiration_date: datetime | None = None


class SupplyResponse(BaseModel):
    id: int
    token: str
    name: str
    description: str | None
    category_id: int
    category: SupplyCategoryBasic
    unit_id: int
    unit: UnitBasic
    available_quantity: float
    min_stock: float
    max_stock: float
    supplier_id: int | None
    expiration_date: datetime | None
    status: str
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None

    class Config:
        from_attributes = True


class DeleteResponseSupply(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int


class ProviderContactCreate(BaseModel):
    name: str
    email: EmailStr | None = None
    phone: str | None = None
    notes: str | None = None


class ProviderContactUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    notes: str | None = None


class ProviderContactResponse(BaseModel):
    id: int
    token: str
    provider_id: int
    name: str
    email: str | None
    phone: str | None
    notes: str | None
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None

    class Config:
        from_attributes = True


class ProviderCreate(BaseModel):
    company: str
    nit: str
    email: EmailStr


class ProviderUpdate(BaseModel):
    company: str | None = None
    nit: str | None = None
    email: EmailStr | None = None


class ProviderResponse(BaseModel):
    id: int
    token: str
    company: str
    nit: str
    email: str
    status: ProviderStatus
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None
    contacts: list[ProviderContactResponse]

    class Config:
        from_attributes = True


class ProviderDeleteResponse(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int


## Esquemas relacionados a ProductCategory
class ProductCategoryBasic(BaseModel):
    id: int
    token: str
    name: str

    class Config:
        from_attributes = True


class CommercialProductBasic(BaseModel):
    id: int
    token: str
    name: str
    status: str

    class Config:
        from_attributes = True


class ProductCategoryCreate(UppercaseMixin, BaseModel):
    name: str
    description: str | None = None


class ProductCategoryUpdate(UppercaseMixin, BaseModel):
    name: str | None = None
    description: str | None = None


class ProductCategoryResponse(BaseModel):
    id: int
    token: str
    name: str
    description: str | None
    status: str
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None
    commercial_products: list[CommercialProductBasic]

    class Config:
        from_attributes = True


class DeleteResponseProductCategory(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int


## Esquemas relacionados a CommercialProduct
class ProviderBasic(BaseModel):
    id: int
    token: str
    company: str

    class Config:
        from_attributes = True


class CommercialProductCreate(UppercaseMixin, BaseModel):
    name: str
    description: str | None = None
    category_id: int
    unit_id: int
    provider_id: int | None = None
    purchase_price: float = 0
    sale_price: float = 0
    available_quantity: float = 0
    min_stock: float = 0
    max_stock: float = 0


class CommercialProductUpdate(UppercaseMixin, BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    unit_id: int | None = None
    provider_id: int | None = None
    purchase_price: float | None = None
    sale_price: float | None = None
    available_quantity: float | None = None
    min_stock: float | None = None
    max_stock: float | None = None


class CommercialProductResponse(BaseModel):
    id: int
    token: str
    name: str
    description: str | None
    category_id: int
    category: ProductCategoryBasic
    unit_id: int
    unit: UnitBasic
    provider_id: int | None
    provider: ProviderBasic | None
    purchase_price: float
    sale_price: float
    available_quantity: float
    min_stock: float
    max_stock: float
    status: str
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None

    class Config:
        from_attributes = True


class DeleteResponseCommercialProduct(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int


## Esquemas relacionados a Recipe (Recetas)
class RecipeIngredientCreate(BaseModel):
    supply_id: int
    quantity: float
    unit_id: int
    notes: str | None = None


class RecipeIngredientResponse(BaseModel):
    id: int
    token: str
    supply_id: int
    supply: SupplyBasic
    quantity: float
    unit_id: int
    unit: UnitBasic
    notes: str | None

    class Config:
        from_attributes = True


class RecipeCreate(UppercaseMixin, BaseModel):
    name: str
    description: str | None = None
    product_id: int
    yield_quantity: float = 1
    yield_unit_id: int
    ingredients: list[RecipeIngredientCreate]


class RecipeUpdate(UppercaseMixin, BaseModel):
    name: str | None = None
    description: str | None = None
    product_id: int | None = None
    yield_quantity: float | None = None
    yield_unit_id: int | None = None
    status: RecipeStatus | None = None
    ingredients: list[RecipeIngredientCreate] | None = None


class RecipeResponse(BaseModel):
    id: int
    token: str
    name: str
    description: str | None
    product_id: int | None
    yield_quantity: float
    yield_unit_id: int
    yield_unit: UnitBasic
    status: RecipeStatus
    ingredients: list[RecipeIngredientResponse]
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None

    class Config:
        from_attributes = True

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v):
        if isinstance(v, str):
            return RecipeStatus(v.lower())
        return v


class DeleteResponseRecipe(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int


## Esquemas relacionados a Production (Producción)
class RecipeBasic(BaseModel):
    id: int
    name: str
    product_id: int | None = None
    yield_quantity: float
    yield_unit: UnitBasic

    class Config:
        from_attributes = True


class ProductionOrderCreate(BaseModel):
    recipe_id: int
    quantity_multiplier: float = Field(gt=0)
    scheduled_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=500)


class ProductionOrderCancelRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class ProductionOrderResponse(BaseModel):
    id: int
    token: str
    recipe_id: int
    recipe: RecipeBasic
    quantity_multiplier: float
    total_yield: float
    status: ProductionOrderStatus
    scheduled_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    notes: str | None
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None

    class Config:
        from_attributes = True

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v):
        if isinstance(v, str):
            return ProductionOrderStatus(v.lower())
        return v


class ProductionOrderStatusChangeResponse(BaseModel):
    message: str
    id: int
    status: ProductionOrderStatus
    changed_at: datetime
    changed_by: int


class ProductionSnapshotResponse(BaseModel):
    id: int
    supply_id: int
    supply: SupplyBasic
    quantity_used: float
    unit_id: int
    unit: UnitBasic
    stock_before: float
    stock_after: float


## Esquemas relacionados a Sales (Ventas)
class UserBasic(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str

    class Config:
        from_attributes = True


class ProductionCompleteResponse(BaseModel):
    message: str
    id: int
    status: ProductionOrderStatus
    total_yield: float
    completed_at: datetime
    product_id: int | None = None
    product_name: str | None = None
    product_quantity_added: float | None = None
    snapshots: list[ProductionSnapshotResponse]
    completed_by: int

    class Config:
        from_attributes = True


class SaleItemCreate(BaseModel):
    item_type: ItemType
    item_id: int
    quantity: float = Field(gt=0)


class SaleCreate(BaseModel):
    items: list[SaleItemCreate] = Field(min_length=1)
    notes: str | None = Field(default=None, max_length=500)


class SaleItemResponse(BaseModel):
    id: int
    token: str
    item_type: ItemType
    item_id: int
    item_name: str
    quantity: float

    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    id: int
    token: str
    user_id: int
    user: UserBasic
    sale_date: datetime
    status: SaleStatus
    notes: str | None
    items: list[SaleItemResponse]
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None

    class Config:
        from_attributes = True

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v):
        if isinstance(v, str):
            return SaleStatus(v.lower())
        return v


class SaleListResponse(BaseModel):
    id: int
    token: str
    user_id: int
    user: UserBasic
    sale_date: datetime
    status: SaleStatus
    notes: str | None
    item_count: int
    total_quantity: float
    created_at: datetime

    class Config:
        from_attributes = True

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v):
        if isinstance(v, str):
            return SaleStatus(v.lower())
        return v


class StockWarning(BaseModel):
    item_type: ItemType
    item_id: int
    item_name: str
    available_quantity: float
    min_stock: float


class SaleListPage(BaseModel):
    items: list[SaleListResponse]
    total: int
    page: int
    limit: int


class SaleCreateResponse(BaseModel):
    sale: SaleResponse
    warnings: list[StockWarning]


class SaleAnnulResponse(BaseModel):
    message: str
    id: int
    status: SaleStatus
    changed_at: datetime
    changed_by: int


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
    tendencia: list[DailySalesPoint]
    top_items: list[TopSaleItem]


class ProductionSection(BaseModel):
    por_estado: list[ProductionByStatusPoint]
    rendimiento_diario: list[DailyProductionPoint]
    top_recetas: list[TopRecipePoint]


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
    productos_stock: list[ProductStockPoint]
    productos_stock_bajo: list[LowStockProduct]
    produccion_por_producto: list[ProductProductionPoint]
    comerciales_stock: list[CommercialStockPoint]
    comerciales_stock_bajo: list[LowStockProduct]
    por_categoria: list[CategoryCountPoint]
    stock_saludable: list[StockHealthPoint]


class DashboardStatsResponse(BaseModel):
    kpis: DashboardKpis
    consumo_tendencia: list[ConsumptionPoint]
    niveles_stock: list[StockLevelPoint]
    stock_bajo: list[LowStockSupplyItem]
    vencidos: list[ExpiringSupplyItem]
    por_vencer: list[ExpiringSupplyItem]
    ventas: SalesSection
    produccion: ProductionSection
    productos: ProductsSection


class InventoryItemStatus(str, Enum):
    LOW = "bajo"
    NORMAL = "normal"
    OVER = "sobre"


class InventoryItem(BaseModel):
    id: int
    item_type: str
    name: str
    description: str | None = None
    category_name: str | None = None
    unit_abbreviation: str | None = None
    available_quantity: float
    min_stock: float
    max_stock: float
    stock_status: InventoryItemStatus
    status: str


class InventorySummary(BaseModel):
    total_items: int
    bajo_stock: int
    sobre_stock: int


class InventoryPage(BaseModel):
    items: list[InventoryItem]
    total: int
    page: int
    limit: int
    summary: InventorySummary


## Esquemas de importación masiva (bulk)
class BulkRowError(BaseModel):
    fila: int
    mensaje: str


class BulkImportResult(BaseModel):
    total: int
    creados: int
    actualizados: int = 0
    errores: list[BulkRowError] = []

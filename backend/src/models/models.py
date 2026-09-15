import uuid
from datetime import datetime
from enum import Enum
from zoneinfo import ZoneInfo

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel

BOGOTA_TZ = ZoneInfo("America/Bogota")


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class User(SQLModel, table=True):
    # Usamos __tablename__ para que la tabla se llame 'users' en plural
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: str = Field(unique=True, index=True, max_length=150)
    phone: str | None = Field(default=None, max_length=20)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    is_admin: bool = Field(default=False)

    # Llave Foránea: Conecta este usuario con un ID de la tabla "roles"
    role_id: int = Field(foreign_key="roles.id")

    # Relación: Permite acceder al objeto Rol directamente (ej. user.role.name)
    role: Role = Relationship(
        back_populates="users", sa_relationship_kwargs={"foreign_keys": "User.role_id"}
    )
    accepted_terms: bool = Field(default=False)
    accepted_terms_at: datetime | None = Field(default=None)

    # Bloqueo temporal por intentos fallidos de inicio de sesión
    failed_login_attempts: int = Field(default=0)
    locked_until: datetime | None = Field(default=None)
    # Relación: Permite relacionar las sessiones del usurio
    sessions: list[SessionApp] = Relationship(back_populates="user")
    password_resets: list[PasswordReset] = Relationship(back_populates="user")

    updated_at: datetime | None = Field(default=None)
    updated_by: int | None = Field(default=None, foreign_key="users.id")
    deleted_at: datetime | None = Field(default=None)
    deleted_by: int | None = Field(default=None, foreign_key="users.id")


class RoleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Role(SQLModel, table=True):
    __tablename__ = "roles"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))

    # -- Auditoria de actualización-------------------
    updated_at: datetime | None = Field(default=None)
    updated_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_role_updated_by"),
            nullable=True,
        ),
    )

    # ── Campos para soft delete ─────────────────────────────
    status: RoleStatus = Field(default=RoleStatus.ACTIVE)
    deleted_at: datetime | None = Field(default=None, nullable=True)
    deleted_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_role_deleted_by"),
            nullable=True,
        ),
    )

    # Relación: Un rol puede tener una lista de muchos usuarios
    users: list[User] = Relationship(
        back_populates="role", sa_relationship_kwargs={"foreign_keys": "[User.role_id]"}
    )
    role_modules: list[RoleModule] = Relationship(back_populates="role")


class SessionApp(SQLModel, table=True):
    __tablename__ = "sessions"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    expires_at: datetime
    is_active: bool = Field(default=True)
    user: User = Relationship(back_populates="sessions")


class PasswordReset(SQLModel, table=True):
    __tablename__ = "password_resets"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(unique=True, index=True, max_length=255)
    user_id: int = Field(foreign_key="users.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    used: bool = Field(default=False)

    user: User = Relationship(back_populates="password_resets")


class Module(SQLModel, table=True):
    __tablename__ = "modules"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    name: str = Field(max_length=100, unique=True)  # "inventario", "ventas", etc.
    label: str = Field(max_length=100)  # "Inventario", "Ventas", etc.
    role_modules: list[RoleModule] = Relationship(back_populates="module")


class RoleModule(SQLModel, table=True):
    __tablename__ = "role_modules"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    role_id: int = Field(foreign_key="roles.id")
    module_id: int = Field(foreign_key="modules.id")

    role: Role = Relationship(back_populates="role_modules")
    module: Module = Relationship(back_populates="role_modules")


class Unit(SQLModel, table=True):
    __tablename__ = "units"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    name: str = Field(max_length=100)
    abbreviation: str = Field(max_length=20)
    description: str | None = Field(default=None, max_length=255)
    quantity: float = Field(default=0)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: int | None = Field(default=None, foreign_key="users.id")
    updated_at: datetime | None = Field(default=None)
    updated_by: int | None = Field(default=None, foreign_key="users.id")
    deleted_at: datetime | None = Field(default=None)
    deleted_by: int | None = Field(default=None, foreign_key="users.id")

    products: list[Product] = Relationship(back_populates="unit")
    supplies: list[Supply] = Relationship(back_populates="unit")
    commercial_products: list[CommercialProduct] = Relationship(
        back_populates="unit",
        sa_relationship_kwargs={"foreign_keys": "[CommercialProduct.unit_id]"},
    )


class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    name: str = Field(max_length=150)
    description: str | None = Field(default=None, max_length=500)
    unit_id: int = Field(foreign_key="units.id")
    available_quantity: float = Field(default=0)
    min_stock: float = Field(default=0)
    max_stock: float = Field(default=0)
    is_locked: bool = Field(default=False)
    status: str = Field(default="active")

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: int | None = Field(default=None, foreign_key="users.id")
    updated_at: datetime | None = Field(default=None)
    updated_by: int | None = Field(default=None, foreign_key="users.id")
    deleted_at: datetime | None = Field(default=None)
    deleted_by: int | None = Field(default=None, foreign_key="users.id")

    unit: Unit = Relationship(back_populates="products")
    recipe: Recipe | None = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"foreign_keys": "[Recipe.product_id]"},
    )


# Modulo de recipes: Categoria de insumos, insumos, estado de receta, receta
# ingrediente receta, estado de orden de produccion, orden produccion
# produccion general
class SupplyCategory(SQLModel, table=True):
    __tablename__ = "supply_categories"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    name: str = Field(max_length=100, unique=True)
    description: str | None = Field(default=None, max_length=255)
    status: str = Field(default="active")

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: int | None = Field(default=None, foreign_key="users.id")
    updated_at: datetime | None = Field(default=None)
    updated_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey(
                "users.id", use_alter=True, name="fk_supply_category_updated_by"
            ),
            nullable=True,
        ),
    )
    deleted_at: datetime | None = Field(default=None)
    deleted_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey(
                "users.id", use_alter=True, name="fk_supply_category_deleted_by"
            ),
            nullable=True,
        ),
    )

    supplies: list[Supply] = Relationship(back_populates="category")


class Supply(SQLModel, table=True):
    __tablename__ = "supplies"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    name: str = Field(max_length=150, unique=True)
    description: str | None = Field(default=None, max_length=500)

    category_id: int = Field(foreign_key="supply_categories.id")
    category: SupplyCategory = Relationship(back_populates="supplies")

    unit_id: int = Field(foreign_key="units.id")
    unit: Unit = Relationship(back_populates="supplies")

    available_quantity: float = Field(default=0)
    min_stock: float = Field(default=0)
    max_stock: float = Field(default=0)
    supplier_id: int | None = Field(default=None, foreign_key="users.id")
    expiration_date: datetime | None = Field(default=None)
    status: str = Field(default="active")

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: int | None = Field(default=None, foreign_key="users.id")
    updated_at: datetime | None = Field(default=None)
    updated_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_supply_updated_by"),
            nullable=True,
        ),
    )
    deleted_at: datetime | None = Field(default=None)
    deleted_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_supply_deleted_by"),
            nullable=True,
        ),
    )

    recipe_ingredients: list[RecipeIngredient] = Relationship(back_populates="supply")


class RecipeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Recipe(SQLModel, table=True):
    __tablename__ = "recipes"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    name: str = Field(max_length=150)
    description: str | None = Field(default=None, max_length=500)

    product_id: int | None = Field(default=None, foreign_key="products.id")
    product: Product | None = Relationship(back_populates="recipe")

    yield_quantity: float = Field(default=1)
    yield_unit_id: int = Field(foreign_key="units.id")
    yield_unit: Unit = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Recipe.yield_unit_id]"}
    )

    status: RecipeStatus = Field(default=RecipeStatus.ACTIVE)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: int | None = Field(default=None, foreign_key="users.id")
    updated_at: datetime | None = Field(default=None)
    updated_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_recipe_updated_by"),
            nullable=True,
        ),
    )
    deleted_at: datetime | None = Field(default=None)
    deleted_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_recipe_deleted_by"),
            nullable=True,
        ),
    )

    ingredients: list[RecipeIngredient] = Relationship(back_populates="recipe")
    production_orders: list[ProductionOrder] = Relationship(back_populates="recipe")


class RecipeIngredient(SQLModel, table=True):
    __tablename__ = "recipe_ingredients"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )

    recipe_id: int = Field(foreign_key="recipes.id")
    recipe: Recipe = Relationship(back_populates="ingredients")

    supply_id: int = Field(foreign_key="supplies.id")
    supply: Supply = Relationship(back_populates="recipe_ingredients")

    quantity: float = Field(default=0)
    unit_id: int = Field(foreign_key="units.id")
    unit: Unit = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[RecipeIngredient.unit_id]"}
    )

    notes: str | None = Field(default=None, max_length=255)


class ProductionOrderStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProductionOrder(SQLModel, table=True):
    __tablename__ = "production_orders"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )

    recipe_id: int = Field(foreign_key="recipes.id")
    recipe: Recipe = Relationship(back_populates="production_orders")

    quantity_multiplier: float = Field(default=1)
    total_yield: float = Field(default=0)

    status: ProductionOrderStatus = Field(default=ProductionOrderStatus.PENDING)

    scheduled_at: datetime | None = Field(default=None)
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    cancelled_at: datetime | None = Field(default=None)
    notes: str | None = Field(default=None, max_length=500)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: int | None = Field(default=None, foreign_key="users.id")
    updated_at: datetime | None = Field(default=None)
    updated_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey(
                "users.id", use_alter=True, name="fk_production_order_updated_by"
            ),
            nullable=True,
        ),
    )
    deleted_at: datetime | None = Field(default=None)
    deleted_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey(
                "users.id", use_alter=True, name="fk_production_order_deleted_by"
            ),
            nullable=True,
        ),
    )

    snapshots: list[ProductionOrderSnapshot] = Relationship(
        back_populates="production_order"
    )


class ProductionOrderSnapshot(SQLModel, table=True):
    __tablename__ = "production_order_snapshots"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )

    production_order_id: int = Field(foreign_key="production_orders.id")
    production_order: ProductionOrder = Relationship(back_populates="snapshots")

    supply_id: int = Field(foreign_key="supplies.id")
    supply: Supply = Relationship()

    quantity_used: float
    unit_id: int = Field(foreign_key="units.id")
    unit: Unit = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ProductionOrderSnapshot.unit_id]"}
    )

    stock_before: float
    stock_after: float


class ProductCategory(SQLModel, table=True):
    __tablename__ = "product_categories"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    name: str = Field(max_length=100, unique=True)
    description: str | None = Field(default=None, max_length=255)
    status: str = Field(default="active")

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: int | None = Field(default=None, foreign_key="users.id")
    updated_at: datetime | None = Field(default=None)
    updated_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey(
                "users.id", use_alter=True, name="fk_product_category_updated_by"
            ),
            nullable=True,
        ),
    )
    deleted_at: datetime | None = Field(default=None)
    deleted_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey(
                "users.id", use_alter=True, name="fk_product_category_deleted_by"
            ),
            nullable=True,
        ),
    )

    commercial_products: list[CommercialProduct] = Relationship(
        back_populates="category"
    )


class CommercialProduct(SQLModel, table=True):
    __tablename__ = "commercial_products"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    name: str = Field(max_length=150)
    description: str | None = Field(default=None, max_length=500)

    category_id: int = Field(foreign_key="product_categories.id")
    category: ProductCategory = Relationship(back_populates="commercial_products")

    unit_id: int = Field(foreign_key="units.id")
    unit: Unit = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[CommercialProduct.unit_id]"}
    )

    provider_id: int | None = Field(default=None, foreign_key="providers.id")
    provider: Provider | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[CommercialProduct.provider_id]"}
    )

    purchase_price: float = Field(default=0)
    sale_price: float = Field(default=0)
    available_quantity: float = Field(default=0)
    min_stock: float = Field(default=0)
    max_stock: float = Field(default=0)
    status: str = Field(default="active")

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: int | None = Field(default=None, foreign_key="users.id")
    updated_at: datetime | None = Field(default=None)
    updated_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey(
                "users.id", use_alter=True, name="fk_commercial_product_updated_by"
            ),
            nullable=True,
        ),
    )
    deleted_at: datetime | None = Field(default=None)
    deleted_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey(
                "users.id", use_alter=True, name="fk_commercial_product_deleted_by"
            ),
            nullable=True,
        ),
    )


class ProviderStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Provider(SQLModel, table=True):
    __tablename__ = "providers"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )

    company: str = Field(max_length=150)
    nit: str = Field(max_length=20, unique=True, index=True)
    email: str = Field(max_length=150, unique=True, index=True)
    status: ProviderStatus = Field(default=ProviderStatus.ACTIVE)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: int | None = Field(default=None, foreign_key="users.id")

    updated_at: datetime | None = Field(default=None)
    updated_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_provider_updated_by"),
            nullable=True,
        ),
    )

    deleted_at: datetime | None = Field(default=None)
    deleted_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_provider_deleted_by"),
            nullable=True,
        ),
    )

    contacts: list[ProviderContact] = Relationship(back_populates="provider")
    commercial_products: list[CommercialProduct] = Relationship(
        back_populates="provider",
        sa_relationship_kwargs={"foreign_keys": "[CommercialProduct.provider_id]"},
    )


class ProviderContact(SQLModel, table=True):
    __tablename__ = "provider_contacts"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )

    provider_id: int = Field(foreign_key="providers.id")
    provider: Provider = Relationship(back_populates="contacts")

    name: str = Field(max_length=150)
    email: str | None = Field(default=None, max_length=150)
    phone: str | None = Field(default=None, max_length=20)
    notes: str | None = Field(default=None, max_length=500)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: int | None = Field(default=None, foreign_key="users.id")

    updated_at: datetime | None = Field(default=None)
    updated_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey(
                "users.id", use_alter=True, name="fk_provider_contact_updated_by"
            ),
            nullable=True,
        ),
    )

    deleted_at: datetime | None = Field(default=None)
    deleted_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey(
                "users.id", use_alter=True, name="fk_provider_contact_deleted_by"
            ),
            nullable=True,
        ),
    )


# Modulo de ventas: venta, item de venta y movimiento de inventario
class SaleStatus(str, Enum):
    COMPLETED = "completada"
    ANNULLED = "anulada"


class ItemType(str, Enum):
    PRODUCT = "product"
    COMMERCIAL = "commercial"
    SUPPLY = "supply"


class MovementType(str, Enum):
    SALE = "sale"
    SALE_ANNULMENT = "sale_annulment"
    ENTRY = "entry"
    MANUAL = "manual"


class Sale(SQLModel, table=True):
    __tablename__ = "sales"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )

    user_id: int = Field(foreign_key="users.id")
    user: User = Relationship(sa_relationship_kwargs={"foreign_keys": "[Sale.user_id]"})

    sale_date: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    status: SaleStatus = Field(default=SaleStatus.COMPLETED)
    notes: str | None = Field(default=None, max_length=500)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: int | None = Field(default=None, foreign_key="users.id")
    updated_at: datetime | None = Field(default=None)
    updated_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_sale_updated_by"),
            nullable=True,
        ),
    )
    deleted_at: datetime | None = Field(default=None)
    deleted_by: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_sale_deleted_by"),
            nullable=True,
        ),
    )

    items: list[SaleItem] = Relationship(back_populates="sale")


class SaleItem(SQLModel, table=True):
    __tablename__ = "sale_items"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )

    sale_id: int = Field(foreign_key="sales.id")
    sale: Sale = Relationship(back_populates="items")

    item_type: ItemType = Field(default=ItemType.PRODUCT)
    item_id: int
    item_name: str = Field(max_length=150)
    quantity: float = Field(default=0)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))


class InventoryMovement(SQLModel, table=True):
    __tablename__ = "inventory_movements"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )

    item_type: ItemType = Field(default=ItemType.PRODUCT)
    item_id: int
    movement_type: MovementType = Field(default=MovementType.SALE)
    quantity: float = Field(default=0)
    stock_before: float = Field(default=0)
    stock_after: float = Field(default=0)

    reference_type: str | None = Field(default=None, max_length=50)
    reference_id: int | None = Field(default=None)

    user_id: int = Field(foreign_key="users.id")
    user: User = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[InventoryMovement.user_id]"}
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Integer, ForeignKey
from enum import Enum
import uuid
from zoneinfo import ZoneInfo

BOGOTA_TZ = ZoneInfo("America/Bogota")


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class User(SQLModel, table=True):
    # Usamos __tablename__ para que la tabla se llame 'users' en plural
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: str = Field(unique=True, index=True, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=20)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    is_admin: bool = Field(default=False)

    # Llave Foránea: Conecta este usuario con un ID de la tabla "roles"
    role_id: int = Field(foreign_key="roles.id")

    # Relación: Permite acceder al objeto Rol directamente (ej. user.role.name)
    role: "Role" = Relationship(
        back_populates="users", sa_relationship_kwargs={"foreign_keys": "User.role_id"}
    )
    accepted_terms: bool = Field(default=False)
    accepted_terms_at: Optional[datetime] = Field(default=None)
    # Relación: Permite relacionar las sessiones del usurio
    sessions: List["SessionApp"] = Relationship(back_populates="user")

    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(default=None, foreign_key="users.id")


class RoleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Role(SQLModel, table=True):
    __tablename__ = "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))

    # -- Auditoria de actualización-------------------
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_role_updated_by"),
            nullable=True,
        ),
    )

    # ── Campos para soft delete ─────────────────────────────
    status: RoleStatus = Field(default=RoleStatus.ACTIVE)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)
    deleted_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_role_deleted_by"),
            nullable=True,
        ),
    )

    # Relación: Un rol puede tener una lista de muchos usuarios
    users: List["User"] = Relationship(
        back_populates="role", sa_relationship_kwargs={"foreign_keys": "[User.role_id]"}
    )

    users: List["User"] = Relationship(
        back_populates="role", sa_relationship_kwargs={"foreign_keys": "[User.role_id]"}
    )
    role_modules: List["RoleModule"] = Relationship(back_populates="role")


class SessionApp(SQLModel, table=True):
    __tablename__ = "sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    expires_at: datetime
    is_active: bool = Field(default=True)
    user: "User" = Relationship(back_populates="sessions")


class PasswordReset(SQLModel, table=True):
    __tablename__ = "password_resets"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(unique=True, index=True, max_length=255)
    user_id: int = Field(foreign_key="users.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    used: bool = Field(default=False)

    user: "User" = Relationship()


class Module(SQLModel, table=True):
    __tablename__ = "modules"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    name: str = Field(max_length=100, unique=True)  # "inventario", "ventas", etc.
    label: str = Field(max_length=100)  # "Inventario", "Ventas", etc.
    role_modules: List["RoleModule"] = Relationship(back_populates="module")


class RoleModule(SQLModel, table=True):
    __tablename__ = "role_modules"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    role_id: int = Field(foreign_key="roles.id")
    module_id: int = Field(foreign_key="modules.id")

    role: "Role" = Relationship(back_populates="role_modules")
    module: "Module" = Relationship(back_populates="role_modules")


class Unit(SQLModel, table=True):
    __tablename__ = "units"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    name: str = Field(max_length=100)
    abbreviation: str = Field(max_length=20)
    description: Optional[str] = Field(default=None, max_length=255)
    quantity: float = Field(default=0)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(default=None, foreign_key="users.id")

    products: List["Product"] = Relationship(back_populates="unit")


class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    name: str = Field(max_length=150)
    description: Optional[str] = Field(default=None, max_length=500)
    unit_id: int = Field(foreign_key="units.id")
    available_quantity: float = Field(default=0)
    min_stock: float = Field(default=0)
    max_stock: float = Field(default=0)
    is_locked: bool = Field(default=False)
    status: str = Field(default="active")

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(default=None, foreign_key="users.id")

    unit: "Unit" = Relationship(back_populates="products")



# Modulo de recipes: Categoria de insumos, insumos, estado de receta, receta
# ingrediente receta, estado de orden de produccion, orden produccion
# produccion general
class SupplyCategory(SQLModel, table=True):
    __tablename__ = "supply_categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    name: str = Field(max_length=100, unique=True)
    description: Optional[str] = Field(default=None, max_length=255)
    status: str = Field(default="active")
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("users.id", use_alter=True, name="fk_supply_category_updated_by"), nullable=True)
    )
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("users.id", use_alter=True, name="fk_supply_category_deleted_by"), nullable=True)
    )

    supplies: List["Supply"] = Relationship(back_populates="category")

class Supply(SQLModel, table=True):
    __tablename__ = "supplies"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    name: str = Field(max_length=150)
    description: Optional[str] = Field(default=None, max_length=500)
    
    category_id: int = Field(foreign_key="supply_categories.id")
    category: "SupplyCategory" = Relationship(back_populates="supplies")

    unit_id: int = Field(foreign_key="units.id")
    unit: "Unit" = Relationship(back_populates="supplies")

    available_quantity: float = Field(default=0)
    min_stock: float = Field(default=0)
    max_stock: float = Field(default=0)
    supplier_id: Optional[int] = Field(default=None, foreign_key="users.id")
    expiration_date: Optional[datetime] = Field(default=None)
    status: str = Field(default="active")

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("users.id", use_alter=True, name="fk_supply_updated_by"), nullable=True)
    )
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("users.id", use_alter=True, name="fk_supply_deleted_by"), nullable=True)
    )

    recipe_ingredients: List["RecipeIngredient"] = Relationship(back_populates="supply")

class RecipeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Recipe(SQLModel, table=True):
    __tablename__ = "recipes"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    name: str = Field(max_length=150)
    description: Optional[str] = Field(default=None, max_length=500)

    product_id: Optional[int] = Field(default=None, foreign_key="products.id")
    product: Optional["Product"] = Relationship(back_populates="recipe")

    yield_quantity: float = Field(default=1)
    yield_unit_id: int = Field(foreign_key="units.id")
    yield_unit: "Unit" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Recipe.yield_unit_id]"}
    )
    
    status: RecipeStatus = Field(default=RecipeStatus.ACTIVE)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("users.id", use_alter=True, name="fk_recipe_updated_by"), nullable=True)
    )
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("users.id", use_alter=True, name="fk_recipe_deleted_by"), nullable=True)
    )

    ingredients: List["RecipeIngredient"] = Relationship(back_populates="recipe")
    production_orders: List["ProductionOrder"] = Relationship(back_populates="recipe")


class RecipeIngredient(SQLModel, table=True):
    __tablename__ = "recipe_ingredients"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)

    recipe_id: int = Field(foreign_key="recipes.id")
    recipe: "Recipe" = Relationship(back_populates="ingredients")

    supply_id: int = Field(foreign_key="supplies.id")
    supply: "Supply" = Relationship(back_populates="recipe_ingredients")

    quantity: float = Field(default=0)
    unit_id: int = Field(foreign_key="units.id")
    unit: "Unit" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[RecipeIngredient.unit_id]"}
    )

    notes: Optional[str] = Field(default=None, max_length=255)

class ProductionOrderStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ProductionOrder(SQLModel, table=True):
    __tablename__ = "production_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)

    recipe_id: int = Field(foreign_key="recipes.id")
    recipe: "Recipe" = Relationship(back_populates="production_orders")

    quantity_multiplier: float = Field(default=1)
    total_yield: float = Field(default=0)

    status: ProductionOrderStatus = Field(default=ProductionOrderStatus.PENDING)

    scheduled_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=500)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("users.id", use_alter=True, name="fk_production_order_updated_by"), nullable=True)
    )
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("users.id", use_alter=True, name="fk_production_order_deleted_by"), nullable=True)
    )

    snapshots: List["ProductionOrderSnapshot"] = Relationship(back_populates="production_order")


class ProductionOrderSnapshot(SQLModel, table=True):
    __tablename__ = "production_order_snapshots"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)

    production_order_id: int = Field(foreign_key="production_orders.id")
    production_order: "ProductionOrder" = Relationship(back_populates="snapshots")

    supply_id: int = Field(foreign_key="supplies.id")
    supply: "Supply" = Relationship()

    quantity_used: float
    unit_id: int = Field(foreign_key="units.id")
    unit: "Unit" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ProductionOrderSnapshot.unit_id]"}
    )

    stock_before: float
    stock_after: float
"""Registro central de modelos.

Importar este módulo garantiza que todas las clases ``table=True`` queden
registradas en ``SQLModel.metadata`` (requerido por Alembic y por la
resolución de relaciones entre módulos).
"""

from src.modules.audit.models import AuditLog  # noqa: F401
from src.modules.commercial_products.models import (  # noqa: F401
    CommercialProduct,
    ProductCategory,
)
from src.modules.inventory.models import InventoryMovement  # noqa: F401
from src.modules.production.models import (  # noqa: F401
    ProductionOrder,
    ProductionOrderSnapshot,
    ProductionOrderStatus,
)
from src.modules.products.models import Product, ProductStatus  # noqa: F401
from src.modules.providers.models import (  # noqa: F401
    Provider,
    ProviderContact,
    ProviderStatus,
)
from src.modules.recipes.models import (  # noqa: F401
    Recipe,
    RecipeIngredient,
    RecipeStatus,
)
from src.modules.roles.models import Module, Role, RoleModule, RoleStatus  # noqa: F401
from src.modules.sales.models import (  # noqa: F401
    ItemType,
    MovementType,
    Sale,
    SaleItem,
    SaleStatus,
)
from src.modules.supplies.models import Supply, SupplyCategory  # noqa: F401
from src.modules.units.models import Unit  # noqa: F401
from src.modules.users.models import (  # noqa: F401
    PasswordReset,
    SessionApp,
    User,
    UserStatus,
)

__all__ = [
    "AuditLog",
    "CommercialProduct",
    "ProductCategory",
    "InventoryMovement",
    "ProductionOrder",
    "ProductionOrderSnapshot",
    "ProductionOrderStatus",
    "Product",
    "ProductStatus",
    "Provider",
    "ProviderContact",
    "ProviderStatus",
    "Recipe",
    "RecipeIngredient",
    "RecipeStatus",
    "Module",
    "Role",
    "RoleModule",
    "RoleStatus",
    "ItemType",
    "MovementType",
    "Sale",
    "SaleItem",
    "SaleStatus",
    "Supply",
    "SupplyCategory",
    "Unit",
    "PasswordReset",
    "SessionApp",
    "User",
    "UserStatus",
]

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from src.models.models import UserStatus, RoleStatus, ProductStatus, ProviderStatus, RecipeStatus
from datetime import datetime


class UppercaseMixin:
    EXCLUDE_FIELDS = {
        "email",
        "description",
        "password",
        "token",
        "new_password",
        "current_password",
        "notas",
        "observaciones",
        "notas",
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
    phone: Optional[str] = None
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
    phone: Optional[str]
    role_id: int
    role: RoleBasic
    is_admin: bool
    status: UserStatus
    created_at: datetime
    accepted_terms: bool
    accepted_terms_at: Optional[datetime]

    class Config:
        from_attributes = True


class DeleteResponseUser(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int


class UserUpdate(UppercaseMixin, BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    is_admin: Optional[bool] = None
    status: Optional[UserStatus] = None 


class UserUpdateResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    role_id: int
    role: RoleBasic
    is_admin: bool
    status: UserStatus
    created_at: datetime
    updated_at: Optional[datetime]
    updated_by: Optional[int]

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
    name: Optional[str] = None
    description: Optional[str] = None


class RolePublic(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    status: RoleStatus
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

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
    description: Optional[str] = None
    quantity: float


class UnitUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None


class UnitResponse(BaseModel):
    id: int
    token: str
    name: str
    abbreviation: str
    description: Optional[str]
    quantity: float
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]

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
    description: Optional[str] = None
    unit_id: int
    available_quantity: float = 0
    min_stock: float = 0
    max_stock: float = 0
    is_locked: bool = False


class ProductUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unit_id: Optional[int] = None
    available_quantity: Optional[float] = None
    min_stock: Optional[float] = None
    max_stock: Optional[float] = None
    is_locked: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    token: str
    name: str
    description: Optional[str]
    unit_id: int
    unit: UnitBasic
    available_quantity: float
    min_stock: float
    max_stock: float
    is_locked: bool
    status: ProductStatus
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]

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
    description: Optional[str] = None


class SupplyCategoryUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class SupplyCategoryResponse(BaseModel):
    id: int
    token: str
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
    supplies: List[SupplyBasic]

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
    description: Optional[str] = None
    category_id: int
    unit_id: int
    available_quantity: float = 0
    min_stock: float = 0
    max_stock: float = 0
    supplier_id: Optional[int] = None
    expiration_date: Optional[datetime] = None


class SupplyUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    unit_id: Optional[int] = None
    available_quantity: Optional[float] = None
    min_stock: Optional[float] = None
    max_stock: Optional[float] = None
    supplier_id: Optional[int] = None
    expiration_date: Optional[datetime] = None


class SupplyResponse(BaseModel):
    id: int
    token: str
    name: str
    description: Optional[str]
    category_id: int
    category: SupplyCategoryBasic
    unit_id: int
    unit: UnitBasic
    available_quantity: float
    min_stock: float
    max_stock: float
    supplier_id: Optional[int]
    expiration_date: Optional[datetime]
    status: str
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]

    class Config:
        from_attributes = True


class DeleteResponseSupply(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int

class ProviderContactCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    notes: Optional[str] = None

class ProviderContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    notes: Optional[str] = None

class ProviderContactResponse(BaseModel):
    id: int
    token: str
    provider_id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    notes: Optional[str]
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
    class Config:
        from_attributes = True

class ProviderCreate(BaseModel):
    company: str
    nit: str
    email: EmailStr

class ProviderUpdate(BaseModel):
    company: Optional[str] = None
    nit: Optional[str] = None
    email: Optional[EmailStr] = None

class ProviderResponse(BaseModel):
    id: int
    token: str
    company: str
    nit: str
    email: str
    status: ProviderStatus
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
    contacts: List[ProviderContactResponse]

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
    description: Optional[str] = None


class ProductCategoryUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProductCategoryResponse(BaseModel):
    id: int
    token: str
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
    commercial_products: List[CommercialProductBasic]

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
    description: Optional[str] = None
    category_id: int
    unit_id: int
    provider_id: Optional[int] = None
    purchase_price: float = 0
    sale_price: float = 0
    available_quantity: float = 0
    min_stock: float = 0
    max_stock: float = 0


class CommercialProductUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    unit_id: Optional[int] = None
    provider_id: Optional[int] = None
    purchase_price: Optional[float] = None
    sale_price: Optional[float] = None
    available_quantity: Optional[float] = None
    min_stock: Optional[float] = None
    max_stock: Optional[float] = None


class CommercialProductResponse(BaseModel):
    id: int
    token: str
    name: str
    description: Optional[str]
    category_id: int
    category: ProductCategoryBasic
    unit_id: int
    unit: UnitBasic
    provider_id: Optional[int]
    provider: Optional[ProviderBasic]
    purchase_price: float
    sale_price: float
    available_quantity: float
    min_stock: float
    max_stock: float
    status: str
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]

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
    notes: Optional[str] = None


class RecipeIngredientResponse(BaseModel):
    id: int
    token: str
    supply_id: int
    supply: SupplyBasic
    quantity: float
    unit_id: int
    unit: UnitBasic
    notes: Optional[str]

    class Config:
        from_attributes = True


class RecipeCreate(UppercaseMixin, BaseModel):
    name: str
    description: Optional[str] = None
    product_id: Optional[int] = None
    yield_quantity: float = 1
    yield_unit_id: int
    ingredients: list[RecipeIngredientCreate]


class RecipeUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    product_id: Optional[int] = None
    yield_quantity: Optional[float] = None
    yield_unit_id: Optional[int] = None
    status: Optional[RecipeStatus] = None
    ingredients: Optional[list[RecipeIngredientCreate]] = None


class RecipeResponse(BaseModel):
    id: int
    token: str
    name: str
    description: Optional[str]
    product_id: Optional[int]
    yield_quantity: float
    yield_unit_id: int
    yield_unit: UnitBasic
    status: RecipeStatus
    ingredients: list[RecipeIngredientResponse]
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]

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
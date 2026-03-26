from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from src.models.models import UserStatus, RoleStatus, ProductStatus
from datetime import datetime


## Esquemas relacionados a Usuarios.
class UserCreate(BaseModel):
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


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    is_admin: Optional[bool] = None


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
class RoleCreate(BaseModel):
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
class RoleUpdate(BaseModel):
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
class UnitCreate(BaseModel):
    name: str
    abbreviation: str
    description: Optional[str] = None
    quantity: float


class UnitUpdate(BaseModel):
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


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    unit_id: int
    available_quantity: float = 0
    min_stock: float = 0
    max_stock: float = 0
    is_locked: bool = False


class ProductUpdate(BaseModel):
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


class SupplyCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class SupplyCategoryUpdate(BaseModel):
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


class SupplyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: int
    unit_id: int
    available_quantity: float = 0
    min_stock: float = 0
    max_stock: float = 0
    supplier_id: Optional[int] = None
    expiration_date: Optional[datetime] = None


class SupplyUpdate(BaseModel):
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

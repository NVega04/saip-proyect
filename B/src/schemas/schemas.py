from pydantic import BaseModel, EmailStr
from typing import Optional
from src.models.models import UserStatus, RoleStatus
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

class LoginResponse(BaseModel):
    session_token: str
    expires_at: datetime
    user: UserResponse

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

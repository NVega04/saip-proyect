from pydantic import BaseModel, EmailStr
from typing import Optional
from src.models.models import UserStatus, RoleStatus
from datetime import datetime

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    position: str
    phone: Optional[str] = None
    role_id: int
    is_admin: bool = False

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    position: str
    phone: Optional[str]
    role_id: int
    is_admin: bool
    status: UserStatus
    created_at: datetime

    class Config:
        from_attributes = True
        

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
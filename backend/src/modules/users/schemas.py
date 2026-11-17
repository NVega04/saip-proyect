from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from src.core.schemas import UppercaseMixin
from src.modules.users.models import UserStatus


class RoleBasic(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UserCreate(UppercaseMixin, BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    role_id: int
    is_admin: bool = False


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

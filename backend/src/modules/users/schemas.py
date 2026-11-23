from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from src.core.schemas import UppercaseMixin
from src.modules.users.models import UserStatus


class RoleBasic(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UserCreate(UppercaseMixin, BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=150)
    phone: Optional[str] = Field(default=None, max_length=20)
    role_id: int = Field(gt=0)
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
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(default=None, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=20)
    role_id: Optional[int] = Field(default=None, gt=0)
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

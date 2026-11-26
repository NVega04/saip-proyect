from datetime import datetime

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
    phone: str | None = None
    role_id: int
    is_admin: bool = False


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

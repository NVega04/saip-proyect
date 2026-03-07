from pydantic import BaseModel, EmailStr
from typing import Optional
from src.models.models import UserStatus
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
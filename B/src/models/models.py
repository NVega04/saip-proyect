from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class User(SQLModel, table=True):
    # Usamos __tablename__ para que la tabla se llame 'users' en plural
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: str = Field(unique=True, index=True, max_length=150)
    position: str = Field(max_length=50)
    phone: Optional[str] = Field(default=None, max_length=20)
    password_hash: str = Field(max_length=255)
    
    # Requisitos específicos
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    is_admin: bool = Field(default=False)
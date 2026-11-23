from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from sqlmodel import Field, Relationship, SQLModel

from src.core.crypto import EncryptedString
from src.core.time import BOGOTA_TZ


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: str = Field(unique=True, index=True, max_length=150)
    phone: Optional[str] = Field(default=None, sa_type=EncryptedString(255))
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    is_admin: bool = Field(default=False)

    role_id: int = Field(foreign_key="roles.id")

    role: "Role" = Relationship(  # noqa: F821
        back_populates="users", sa_relationship_kwargs={"foreign_keys": "User.role_id"}
    )
    accepted_terms: bool = Field(default=False)
    accepted_terms_at: Optional[datetime] = Field(default=None)

    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = Field(default=None)

    sessions: List["SessionApp"] = Relationship(back_populates="user")
    password_resets: List["PasswordReset"] = Relationship(back_populates="user")

    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(default=None, foreign_key="users.id")


class SessionApp(SQLModel, table=True):
    __tablename__ = "sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    expires_at: datetime
    is_active: bool = Field(default=True)
    user: "User" = Relationship(back_populates="sessions")


class PasswordReset(SQLModel, table=True):
    __tablename__ = "password_resets"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(unique=True, index=True, max_length=255)
    user_id: int = Field(foreign_key="users.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    used: bool = Field(default=False)

    user: "User" = Relationship(back_populates="password_resets")

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel

from src.core.time import BOGOTA_TZ


class RoleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Role(SQLModel, table=True):
    __tablename__ = "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))

    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_role_updated_by"),
            nullable=True,
        ),
    )

    status: RoleStatus = Field(default=RoleStatus.ACTIVE)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)
    deleted_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_role_deleted_by"),
            nullable=True,
        ),
    )

    users: List["User"] = Relationship(  # noqa: F821
        back_populates="role", sa_relationship_kwargs={"foreign_keys": "[User.role_id]"}
    )
    role_modules: List["RoleModule"] = Relationship(back_populates="role")


class Module(SQLModel, table=True):
    __tablename__ = "modules"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)
    name: str = Field(max_length=100, unique=True)
    label: str = Field(max_length=100)
    role_modules: List["RoleModule"] = Relationship(back_populates="module")


class RoleModule(SQLModel, table=True):
    __tablename__ = "role_modules"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)
    role_id: int = Field(foreign_key="roles.id")
    module_id: int = Field(foreign_key="modules.id")

    role: "Role" = Relationship(back_populates="role_modules")
    module: "Module" = Relationship(back_populates="role_modules")

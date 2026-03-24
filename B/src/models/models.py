from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Integer, ForeignKey
from enum import Enum
import uuid

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class User(SQLModel, table=True):
    # Usamos __tablename__ para que la tabla se llame 'users' en plural
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: str = Field(unique=True, index=True, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=20)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    is_admin: bool = Field(default=False)

    # Llave Foránea: Conecta este usuario con un ID de la tabla "roles"
    role_id: int = Field(foreign_key="roles.id")
    
    # Relación: Permite acceder al objeto Rol directamente (ej. user.role.name)
    role: "Role" = Relationship(back_populates="users", sa_relationship_kwargs={"foreign_keys": "User.role_id"})

    #Relación: Permite relacionar las sessiones del usurio
    sessions: List["SessionApp"] = Relationship(back_populates="user")

    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(default=None, foreign_key="users.id")
      
class RoleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Role(SQLModel, table=True):
    
    __tablename__= "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
    
    # -- Auditoria de actualización-------------------
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("users.id", use_alter=True, name="fk_role_updated_by"), nullable=True)
    )

    # ── Campos para soft delete ─────────────────────────────
    status: RoleStatus = Field(default=RoleStatus.ACTIVE) 
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)
    deleted_by: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("users.id", use_alter=True, name="fk_role_deleted_by"), nullable=True)
    )
    
    # Relación: Un rol puede tener una lista de muchos usuarios
    users: List["User"] = Relationship(
        back_populates="role",
        sa_relationship_kwargs={"foreign_keys": "[User.role_id]"}
        )
    
    users: List["User"] = Relationship(
        back_populates="role",
        sa_relationship_kwargs={"foreign_keys": "[User.role_id]"}
    )
    role_modules: List["RoleModule"] = Relationship(back_populates="role")

class SessionApp(SQLModel, table=True):
    __tablename__ = "sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    is_active: bool = Field(default=True)
    user: "User" = Relationship(back_populates="sessions")

class PasswordReset(SQLModel, table=True):
    __tablename__ = "password_resets"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(unique=True, index=True, max_length=255)
    user_id: int = Field(foreign_key="users.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    used: bool = Field(default=False)

    user: "User" = Relationship()

class Module(SQLModel, table=True):
    __tablename__ = "modules"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    name: str = Field(max_length=100, unique=True)   # "inventario", "ventas", etc.
    label: str = Field(max_length=100)               # "Inventario", "Ventas", etc.
    role_modules: List["RoleModule"] = Relationship(back_populates="module")

class RoleModule(SQLModel, table=True):
    __tablename__ = "role_modules"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    role_id: int = Field(foreign_key="roles.id")
    module_id: int = Field(foreign_key="modules.id")

    role: "Role" = Relationship(back_populates="role_modules")
    module: "Module" = Relationship(back_populates="role_modules")
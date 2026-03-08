from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
import uuid

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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    is_admin: bool = Field(default=False)

    # Llave Foránea: Conecta este usuario con un ID de la tabla "roles"
    role_id: int = Field(foreign_key="roles.id")
    
    # Relación: Permite acceder al objeto Rol directamente (ej. user.role.name)
    role: "Role" = Relationship(back_populates="users")

    #Relación: Permite relacionar las sessiones del usurio
    sessions: List["Session"] = Relationship(back_populates="user")

class Role(SQLModel, table=True):
    
    __tablename__= "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    create_date: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
    # Relación: Un rol puede tener una lista de muchos usuarios
    users: List["User"] = Relationship(back_populates="role")

class Session(SQLModel, table=True):
    __tablename__ = "sessions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    is_active: bool = Field(default=True)

    user: "User" = Relationship(back_populates="sessions")
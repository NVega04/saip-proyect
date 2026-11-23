from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.core.schemas import UppercaseMixin
from src.modules.roles.models import RoleStatus


class RoleCreate(UppercaseMixin, BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=500)


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


class RoleUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


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


class ModuleResponse(BaseModel):
    id: int
    token: str
    name: str
    label: str

    class Config:
        from_attributes = True


class RoleModuleAssign(BaseModel):
    module_ids: list[int] = Field(min_length=1)


class RoleModuleResponse(BaseModel):
    id: int
    token: str
    role_id: int
    module_id: int
    module: ModuleResponse

    class Config:
        from_attributes = True

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.core.schemas import UppercaseMixin
from src.modules.roles.models import RoleStatus


class RoleCreate(UppercaseMixin, BaseModel):
    name: str
    description: str


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


class RoleUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


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
    module_ids: list[int]


class RoleModuleResponse(BaseModel):
    id: int
    token: str
    role_id: int
    module_id: int
    module: ModuleResponse

    class Config:
        from_attributes = True

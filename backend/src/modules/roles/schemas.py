from datetime import datetime

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
    name: str | None = None
    description: str | None = None


class RolePublic(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    status: RoleStatus
    updated_at: datetime | None = None
    updated_by: int | None = None
    deleted_at: datetime | None = None
    deleted_by: int | None = None

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

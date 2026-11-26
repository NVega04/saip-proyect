from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr

from src.modules.providers.models import ProviderStatus


class ProviderContactCreate(BaseModel):
    name: str
    email: EmailStr | None = None
    phone: str | None = None
    notes: str | None = None


class ProviderContactUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    notes: str | None = None


class ProviderContactResponse(BaseModel):
    id: int
    token: str
    provider_id: int
    name: str
    email: str | None
    phone: str | None
    notes: str | None
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None

    class Config:
        from_attributes = True


class ProviderCreate(BaseModel):
    company: str
    nit: str
    email: EmailStr


class ProviderUpdate(BaseModel):
    company: str | None = None
    nit: str | None = None
    email: EmailStr | None = None


class ProviderResponse(BaseModel):
    id: int
    token: str
    company: str
    nit: str
    email: str
    status: ProviderStatus
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None
    contacts: List[ProviderContactResponse]

    class Config:
        from_attributes = True


class ProviderDeleteResponse(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int

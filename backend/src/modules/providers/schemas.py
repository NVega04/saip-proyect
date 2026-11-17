from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from src.modules.providers.models import ProviderStatus


class ProviderContactCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class ProviderContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class ProviderContactResponse(BaseModel):
    id: int
    token: str
    provider_id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    notes: Optional[str]
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]

    class Config:
        from_attributes = True


class ProviderCreate(BaseModel):
    company: str
    nit: str
    email: EmailStr


class ProviderUpdate(BaseModel):
    company: Optional[str] = None
    nit: Optional[str] = None
    email: Optional[EmailStr] = None


class ProviderResponse(BaseModel):
    id: int
    token: str
    company: str
    nit: str
    email: str
    status: ProviderStatus
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
    contacts: List[ProviderContactResponse]

    class Config:
        from_attributes = True


class ProviderDeleteResponse(BaseModel):
    message: str
    deleted_at: datetime
    deleted_by: int

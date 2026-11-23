from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from src.modules.providers.models import ProviderStatus


class ProviderContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: Optional[EmailStr] = Field(default=None, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=20)
    notes: Optional[str] = Field(default=None, max_length=500)


class ProviderContactUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    email: Optional[EmailStr] = Field(default=None, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=20)
    notes: Optional[str] = Field(default=None, max_length=500)


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
    company: str = Field(min_length=1, max_length=150)
    nit: str = Field(min_length=1, max_length=20)
    email: EmailStr = Field(max_length=150)


class ProviderUpdate(BaseModel):
    company: Optional[str] = Field(default=None, min_length=1, max_length=150)
    nit: Optional[str] = Field(default=None, min_length=1, max_length=20)
    email: Optional[EmailStr] = Field(default=None, max_length=150)


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

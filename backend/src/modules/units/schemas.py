from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.core.schemas import UppercaseMixin


class UnitCreate(UppercaseMixin, BaseModel):
    name: str = Field(min_length=1, max_length=100)
    abbreviation: str = Field(min_length=1, max_length=20)
    description: Optional[str] = Field(default=None, max_length=255)
    quantity: float = Field(ge=0)


class UnitUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    abbreviation: Optional[str] = Field(default=None, min_length=1, max_length=20)
    description: Optional[str] = Field(default=None, max_length=255)
    quantity: Optional[float] = Field(default=None, ge=0)


class UnitResponse(BaseModel):
    id: int
    token: str
    name: str
    abbreviation: str
    description: Optional[str]
    quantity: float
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]

    class Config:
        from_attributes = True


class UnitBasic(BaseModel):
    id: int
    name: str
    abbreviation: str

    class Config:
        from_attributes = True

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.core.schemas import UppercaseMixin


class UnitCreate(UppercaseMixin, BaseModel):
    name: str
    abbreviation: str
    description: Optional[str] = None
    quantity: float


class UnitUpdate(UppercaseMixin, BaseModel):
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None


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

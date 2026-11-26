from datetime import datetime

from pydantic import BaseModel

from src.core.schemas import UppercaseMixin


class UnitCreate(UppercaseMixin, BaseModel):
    name: str
    abbreviation: str
    description: str | None = None
    quantity: float


class UnitUpdate(UppercaseMixin, BaseModel):
    name: str | None = None
    abbreviation: str | None = None
    description: str | None = None
    quantity: float | None = None


class UnitResponse(BaseModel):
    id: int
    token: str
    name: str
    abbreviation: str
    description: str | None
    quantity: float
    created_at: datetime
    created_by: int | None
    updated_at: datetime | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None

    class Config:
        from_attributes = True


class UnitBasic(BaseModel):
    id: int
    name: str
    abbreviation: str

    class Config:
        from_attributes = True

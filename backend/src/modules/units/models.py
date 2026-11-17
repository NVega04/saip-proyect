from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlmodel import Field, Relationship, SQLModel

from src.core.time import BOGOTA_TZ


class Unit(SQLModel, table=True):
    __tablename__ = "units"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True)
    name: str = Field(max_length=100)
    abbreviation: str = Field(max_length=20)
    description: Optional[str] = Field(default=None, max_length=255)
    quantity: float = Field(default=0)

    created_at: datetime = Field(default_factory=lambda: datetime.now(BOGOTA_TZ))
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(default=None, foreign_key="users.id")

    products: List["Product"] = Relationship(back_populates="unit")  # noqa: F821
    supplies: List["Supply"] = Relationship(back_populates="unit")  # noqa: F821
    commercial_products: List["CommercialProduct"] = Relationship(  # noqa: F821
        back_populates="unit",
        sa_relationship_kwargs={"foreign_keys": "[CommercialProduct.unit_id]"},
    )

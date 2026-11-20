from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(
        default=None, foreign_key="users.id", index=True
    )
    action: str = Field(max_length=100, index=True)
    resource_type: str = Field(max_length=100)
    resource_id: Optional[int] = Field(default=None, index=True)
    old_value: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    new_value: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    ip_address: Optional[str] = Field(default=None, max_length=45)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), index=True
    )

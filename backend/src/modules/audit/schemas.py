from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    resource_type: str
    resource_id: Optional[int]
    old_value: Optional[dict[str, Any]]
    new_value: Optional[dict[str, Any]]
    ip_address: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditLogPage(BaseModel):
    items: list[AuditLogResponse]
    total: int
    page: int
    limit: int

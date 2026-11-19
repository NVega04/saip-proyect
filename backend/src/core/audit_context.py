from dataclasses import dataclass
from typing import Optional

from fastapi import Request


@dataclass(frozen=True)
class AuditContext:
    ip_address: Optional[str] = None


def get_audit_context(request: Request) -> AuditContext:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return AuditContext(ip_address=forwarded.split(",", 1)[0].strip() or None)
    return AuditContext(ip_address=request.client.host if request.client else None)

import re
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional

from sqlmodel import Session, select

from src.modules.audit.models import AuditLog
from src.modules.audit.schemas import AuditLogPage, AuditLogResponse

SENSITIVE_KEY_PATTERN = re.compile(
    r"(password|passwd|secret|token|hash|jwt|credential|authorization|reset)",
    re.IGNORECASE,
)


def sanitize_audit_value(value: Any) -> Any:
    """Elimina de forma recursiva cualquier campo sensible del registro."""
    if isinstance(value, Mapping):
        return {
            str(key): sanitize_audit_value(item)
            for key, item in value.items()
            if not SENSITIVE_KEY_PATTERN.search(str(key))
        }
    if isinstance(value, (list, tuple, set)):
        return [sanitize_audit_value(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


class AuditService:
    """Escritura de auditoría; los routers nunca la invocan directamente."""

    def __init__(self, session: Session, ip_address: Optional[str] = None):
        self.session = session
        self.ip_address = ip_address

    def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        old_value: Optional[dict[str, Any]] = None,
        new_value: Optional[dict[str, Any]] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        commit: bool = False,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=sanitize_audit_value(old_value) if old_value is not None else None,
            new_value=sanitize_audit_value(new_value) if new_value is not None else None,
            ip_address=ip_address if ip_address is not None else self.ip_address,
            timestamp=datetime.now(timezone.utc),
        )
        self.session.add(entry)
        self.session.flush()
        if commit:
            self.session.commit()
            self.session.refresh(entry)
        return entry


class AuditReadService:
    """Lectura paginada y append-only del log de auditoría."""

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _to_response(entry: AuditLog) -> AuditLogResponse:
        data = AuditLogResponse.model_validate(entry).model_dump()
        for key in ("old_value", "new_value"):
            if data[key] is not None:
                data[key] = sanitize_audit_value(data[key])
        return AuditLogResponse.model_validate(data)

    def list(
        self,
        page: int,
        limit: int,
        action: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> AuditLogPage:
        query = select(AuditLog)
        if action:
            query = query.where(AuditLog.action == action)
        if user_id is not None:
            query = query.where(AuditLog.user_id == user_id)

        total = len(self.session.exec(query).all())
        entries = self.session.exec(
            query.order_by(AuditLog.timestamp.desc(), AuditLog.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        ).all()

        return AuditLogPage(
            items=[self._to_response(entry) for entry in entries],
            total=total,
            page=page,
            limit=limit,
        )

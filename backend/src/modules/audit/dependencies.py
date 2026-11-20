from fastapi import Depends
from sqlmodel import Session

from src.core.audit_context import AuditContext, get_audit_context
from src.core.database import get_session
from src.modules.audit.service import AuditReadService, AuditService


def get_audit_service(
    session: Session = Depends(get_session),
    context: AuditContext = Depends(get_audit_context),
) -> AuditService:
    return AuditService(session, ip_address=context.ip_address)


def get_audit_read_service(session: Session = Depends(get_session)) -> AuditReadService:
    return AuditReadService(session)

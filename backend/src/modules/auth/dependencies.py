from fastapi import Depends
from sqlmodel import Session

from src.core.audit_context import AuditContext, get_audit_context
from src.core.database import get_session
from src.modules.auth.service import AuthService


def get_auth_service(
    session: Session = Depends(get_session),
    context: AuditContext = Depends(get_audit_context),
) -> AuthService:
    return AuthService(session, ip_address=context.ip_address)

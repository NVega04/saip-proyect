from fastapi import Depends
from sqlmodel import Session

from src.core.audit_context import AuditContext, get_audit_context
from src.core.database import get_session
from src.modules.users.service import UsersService


def get_users_service(
    session: Session = Depends(get_session),
    context: AuditContext = Depends(get_audit_context),
) -> UsersService:
    return UsersService(session, ip_address=context.ip_address)

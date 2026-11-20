from fastapi import Depends
from sqlmodel import Session

from src.core.audit_context import AuditContext, get_audit_context
from src.core.database import get_session
from src.modules.roles.service import RoleModulesService, RolesService


def get_roles_service(
    session: Session = Depends(get_session),
    context: AuditContext = Depends(get_audit_context),
) -> RolesService:
    return RolesService(session, ip_address=context.ip_address)


def get_role_modules_service(
    session: Session = Depends(get_session),
    context: AuditContext = Depends(get_audit_context),
) -> RoleModulesService:
    return RoleModulesService(session, ip_address=context.ip_address)

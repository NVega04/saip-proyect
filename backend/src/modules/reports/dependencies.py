from fastapi import Depends
from sqlmodel import Session

from src.core.audit_context import AuditContext, get_audit_context
from src.core.database import get_session
from src.modules.reports.service import ReportsService


def get_reports_service(
    session: Session = Depends(get_session),
    context: AuditContext = Depends(get_audit_context),
) -> ReportsService:
    return ReportsService(session, ip_address=context.ip_address)

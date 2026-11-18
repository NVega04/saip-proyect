from fastapi import Depends
from sqlmodel import Session

from src.core.database import get_session
from src.modules.reports.service import ReportsService


def get_reports_service(session: Session = Depends(get_session)) -> ReportsService:
    return ReportsService(session)

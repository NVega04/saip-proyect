from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.core.dependencies import get_current_user
from src.modules.reports.dependencies import get_reports_service
from src.modules.reports.service import ReportsService
from src.modules.users.models import User

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/{entity}",
    summary="Generar reporte por entidad (Excel o JSON)",
)
def generate_report(
    entity: str,
    fecha_inicio: Optional[date] = Query(default=None),
    fecha_fin: Optional[date] = Query(default=None),
    status: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None, max_length=150),
    format: str = Query(default="xlsx", pattern="^(xlsx|json)$"),
    service: ReportsService = Depends(get_reports_service),
    current_user: User = Depends(get_current_user),
):
    return service.generate(
        entity, fecha_inicio, fecha_fin, status, search, format
    )

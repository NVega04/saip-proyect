from fastapi import APIRouter, Depends, Query, status

from src.core.dependencies import get_current_user
from src.modules.stats.dependencies import get_stats_service
from src.modules.stats.schemas import DashboardStatsResponse
from src.modules.stats.service import StatsService
from src.modules.users.models import User

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get(
    "/dashboard",
    response_model=DashboardStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Estadísticas agregadas de insumos para el dashboard",
)
def get_dashboard(
    days: int = Query(default=30, ge=1, le=365),
    service: StatsService = Depends(get_stats_service),
    current_user: User = Depends(get_current_user),
):
    return service.dashboard(days)

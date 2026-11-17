from fastapi import Depends
from sqlmodel import Session

from src.core.database import get_session
from src.modules.stats.service import StatsService


def get_stats_service(session: Session = Depends(get_session)) -> StatsService:
    return StatsService(session)

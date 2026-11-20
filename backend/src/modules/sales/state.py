from datetime import datetime, timedelta, timezone
from typing import FrozenSet, Optional

from src.core.exceptions import BusinessRuleError
from src.core.time import BOGOTA_TZ
from src.modules.sales.models import SaleStatus

ALLOWED_TRANSITIONS: dict[SaleStatus, FrozenSet[SaleStatus]] = {
    SaleStatus.COMPLETED: frozenset({SaleStatus.ANNULLED}),
    SaleStatus.ANNULLED: frozenset(),
}

ANNULMENT_WINDOW_HOURS = 24


def ensure_transition(current: SaleStatus, target: SaleStatus) -> None:
    if target not in ALLOWED_TRANSITIONS.get(current, frozenset()):
        raise BusinessRuleError(
            f"Transición no permitida: '{current.value}' a '{target.value}'."
        )


def to_utc(value: datetime) -> datetime:
    """Interpreta fechas naive de MySQL como hora de Bogotá y las convierte."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=BOGOTA_TZ)
    return value.astimezone(timezone.utc)


def ensure_annulment_window(
    sale_date: datetime, now: Optional[datetime] = None
) -> None:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    if current - to_utc(sale_date) > timedelta(hours=ANNULMENT_WINDOW_HOURS):
        raise BusinessRuleError("Solo se pueden anular ventas dentro de 24 horas")

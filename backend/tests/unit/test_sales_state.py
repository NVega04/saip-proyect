from datetime import datetime, timezone

import pytest

from src.core.exceptions import BusinessRuleError
from src.core.time import BOGOTA_TZ
from src.modules.sales.models import SaleStatus
from src.modules.sales.state import (
    ensure_annulment_window,
    ensure_transition,
    to_utc,
)


def test_completed_can_transition_to_annulled() -> None:
    ensure_transition(SaleStatus.COMPLETED, SaleStatus.ANNULLED)


def test_annulled_cannot_be_annulled_again() -> None:
    with pytest.raises(BusinessRuleError, match="Transición no permitida"):
        ensure_transition(SaleStatus.ANNULLED, SaleStatus.ANNULLED)


def test_naive_sale_date_is_interpreted_as_bogota() -> None:
    assert to_utc(datetime(2026, 1, 1, 12, 0)) == datetime(
        2026, 1, 1, 17, 0, tzinfo=timezone.utc
    )


def test_annulment_within_24_hours_is_allowed() -> None:
    sale_date = datetime(2026, 1, 1, 12, 0, tzinfo=BOGOTA_TZ)
    now = datetime(2026, 1, 2, 17, 0, tzinfo=timezone.utc)

    ensure_annulment_window(sale_date, now)


def test_annulment_after_24_hours_is_rejected() -> None:
    sale_date = datetime(2026, 1, 1, 12, 0, tzinfo=BOGOTA_TZ)
    now = datetime(2026, 1, 2, 17, 0, 1, tzinfo=timezone.utc)

    with pytest.raises(BusinessRuleError, match="24 horas"):
        ensure_annulment_window(sale_date, now)


def test_annulment_with_naive_dates_uses_utc_comparison() -> None:
    ensure_annulment_window(
        datetime(2026, 1, 1, 12, 0),
        datetime(2026, 1, 2, 12, 0, 1),
    )

    with pytest.raises(BusinessRuleError):
        ensure_annulment_window(
            datetime(2026, 1, 1, 12, 0),
            datetime(2026, 1, 2, 17, 0, 1),
        )

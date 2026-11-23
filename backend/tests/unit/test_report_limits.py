"""Regresiones de los límites de los reportes de la Fase 3."""

from datetime import date

import pytest

from src.modules.reports.service import REPORT_ROW_LIMIT, _validate_date_range
from src.core.exceptions import UnprocessableError


@pytest.mark.unit
def test_row_limit_is_bounded():
    assert 0 < REPORT_ROW_LIMIT <= 10_000


@pytest.mark.unit
def test_high_volume_entities_require_date_range():
    with pytest.raises(UnprocessableError):
        _validate_date_range("sessions", None, None)
    with pytest.raises(UnprocessableError):
        _validate_date_range("production", None, None)


@pytest.mark.unit
def test_date_range_order_and_span_are_validated():
    with pytest.raises(UnprocessableError):
        _validate_date_range("products", date(2026, 2, 1), date(2026, 1, 1))
    with pytest.raises(UnprocessableError):
        _validate_date_range("products", date(2020, 1, 1), date(2026, 1, 1))


@pytest.mark.unit
def test_report_without_dates_still_works(client, admin_headers):
    response = client.get("/reports/products?format=json", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["filters_applied"]["truncado"] is False


@pytest.mark.unit
def test_sessions_report_without_dates_is_rejected(client, admin_headers):
    response = client.get("/reports/sessions?format=json", headers=admin_headers)
    assert response.status_code == 422

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.core.config import Settings
from src.core.password import PASSWORD_HINTS, password_errors
from src.core.security import generate_temp_password
from src.modules.audit.service import sanitize_audit_value
from src.modules.sales.models import SaleStatus
from src.modules.sales.state import ensure_annulment_window, ensure_transition

BACKEND_DIR = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.regression


def test_regression_phase2_jwt_secret_minimum(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "demasiado-corto")

    with pytest.raises(ValidationError, match="al menos 32"):
        Settings(_env_file=None, frontend_url="http://localhost:5173")


def test_regression_phase2_no_default_jwt_secret():
    source = (BACKEND_DIR / "src/core/security.py").read_text()

    assert "cambiar-en-produccion" not in source
    assert "settings.jwt_secret" in source


def test_regression_phase2_cors_is_configurable(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173/, https://saip.lat")

    config = Settings(
        _env_file=None,
        jwt_secret="test-jwt-secret-con-al-menos-32-caracteres",
        frontend_url="http://localhost:5173",
    )

    assert config.cors_origins == ["http://localhost:5173", "https://saip.lat"]
    assert all("*" not in origin for origin in config.cors_origins)


def test_regression_phase2_password_policy():
    assert password_errors("Panaderia12!") == []
    assert "Mínimo 12 caracteres" in password_errors("Todo123!")


def test_regression_phase2_temporary_password_is_safe():
    password = generate_temp_password()
    source = (BACKEND_DIR / "src/core/security.py").read_text()

    assert password_errors(password) == []
    assert "logger" not in source


def test_regression_phase2_password_hints_match_frontend_contract():
    assert PASSWORD_HINTS == (
        "Mínimo 12 caracteres",
        "Al menos una mayúscula",
        "Al menos una minúscula",
        "Al menos un número",
        "Al menos un carácter especial",
    )


def test_regression_phase2_email_links_come_from_settings():
    source = (BACKEND_DIR / "src/core/email.py").read_text()

    assert "frontend_link" in source
    assert "http://localhost:5173" not in source


def test_regression_phase4_audit_values_are_sanitized():
    value = {
        "password": "secreto",
        "nested": {"session_token": "abc", "safe_field": "visible"},
        "items": [{"api_secret": "xyz", "amount": 10}],
    }

    assert sanitize_audit_value(value) == {
        "nested": {"safe_field": "visible"},
        "items": [{"amount": 10}],
    }


def test_regression_phase4_annulment_rules_are_enforced():
    ensure_transition(SaleStatus.COMPLETED, SaleStatus.ANNULLED)

    with pytest.raises(Exception, match="Transición no permitida"):
        ensure_transition(SaleStatus.ANNULLED, SaleStatus.COMPLETED)

    now = datetime.now(timezone.utc)
    with pytest.raises(Exception, match="24 horas"):
        ensure_annulment_window(now - timedelta(hours=24, seconds=1), now)

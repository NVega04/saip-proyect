"""Tests de la política de contraseñas (Fase 2)."""

import logging
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.core.exceptions import BusinessRuleError
from src.core.password import PASSWORD_HINTS, password_errors, validate_password
from src.core.security import generate_temp_password
from src.modules.auth.schemas import ChangePasswordRequest, ResetPasswordRequest
from src.modules.users.schemas import UserCreate
from src.modules.users.service import UsersService

STRONG_PASSWORD = "Panaderia2026!"


def test_strong_password_has_no_errors():
    assert password_errors(STRONG_PASSWORD) == []
    assert validate_password(STRONG_PASSWORD) == STRONG_PASSWORD


def test_weak_password_reports_every_unmet_rule():
    assert password_errors("") == list(PASSWORD_HINTS)


def test_validate_password_raises_business_rule_error():
    with pytest.raises(BusinessRuleError, match="Mínimo 12 caracteres"):
        validate_password("Todo123!")


def test_reset_schema_rejects_weak_password():
    with pytest.raises(ValidationError, match="Mínimo 12 caracteres"):
        ResetPasswordRequest(token="abc", new_password="debil")

    body = ResetPasswordRequest(token="abc", new_password=STRONG_PASSWORD)
    assert body.new_password == STRONG_PASSWORD


def test_change_schema_rejects_weak_password():
    with pytest.raises(ValidationError, match="Al menos un carácter especial"):
        ChangePasswordRequest(
            current_password="Prueba123!", new_password="Panaderia2026"
        )


def test_generated_temp_password_meets_policy():
    for _ in range(25):
        assert password_errors(generate_temp_password()) == []


def test_create_user_does_not_log_temp_password(
    db_session, admin_role, monkeypatch, caplog
):
    sentinel = "TempPassword123!"
    monkeypatch.setattr(
        "src.modules.users.service.generate_temp_password", lambda: sentinel
    )
    monkeypatch.setattr("src.modules.users.service.send_welcome_email", lambda *a: None)

    with caplog.at_level(logging.DEBUG):
        UsersService(db_session).create(
            UserCreate(
                first_name="Ana",
                last_name="Prueba",
                email=f"temp-{uuid4().hex[:8]}@saip.com",
                role_id=admin_role.id,
            )
        )

    assert sentinel not in caplog.text


def test_change_password_endpoint_rejects_weak_password(client, admin_headers):
    response = client.post(
        "/session/change-password",
        headers=admin_headers,
        json={"current_password": "Prueba123!", "new_password": "debil"},
    )

    assert response.status_code == 422

import pytest

from src.core.security import decode_jwt
from src.modules.auth import router as auth_router
from tests.conftest import TEST_USER_PASSWORD

pytestmark = pytest.mark.security


def test_login_success_returns_valid_session(client, admin_user):
    response = client.post(
        "/session/login",
        json={"email": admin_user.email, "password": TEST_USER_PASSWORD},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == admin_user.email
    assert data["terms_required"] is False

    payload = decode_jwt(data["session_token"])
    assert payload is not None
    assert payload["sub"] == str(admin_user.id)


def test_login_failure_with_unknown_email(client):
    response = client.post(
        "/session/login",
        json={"email": "usuario_inexistente@saip.com", "password": "clave_incorrecta_123"},
    )

    assert response.status_code == 401
    assert "Credenciales inválidas" in response.json()["detail"]


def test_login_failure_with_wrong_password(client, admin_user):
    response = client.post(
        "/session/login",
        json={"email": admin_user.email, "password": "clave_incorrecta_123"},
    )

    assert response.status_code == 401
    assert "Credenciales inválidas" in response.json()["detail"]


def test_login_rate_limit_blocks_sixth_attempt(client, monkeypatch):
    monkeypatch.setattr(auth_router.limiter, "enabled", True)
    auth_router.limiter.reset()

    payload = {
        "email": "usuario_inexistente@saip.com",
        "password": "clave_incorrecta_123",
    }
    for _ in range(5):
        response = client.post("/session/login", json=payload)
        assert response.status_code == 401

    response = client.post("/session/login", json=payload)

    assert response.status_code == 429

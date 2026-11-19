"""Tests del manejo del secreto JWT (Fase 2)."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt

from src.core import security
from src.core.config import settings

BACKEND_DIR = Path(__file__).resolve().parents[2]


def _expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=1)


def test_jwt_uses_configured_secret_without_fallback():
    assert security.JWT_SECRET == settings.jwt_secret
    assert security.JWT_SECRET != "cambiar-en-produccion"

    for filename in ("src/core/security.py", "src/core/config.py"):
        assert "cambiar-en-produccion" not in (BACKEND_DIR / filename).read_text()


def test_create_and_decode_jwt():
    token = security.create_jwt("session-123", 7, _expiry())

    payload = security.decode_jwt(token)

    assert payload is not None
    assert payload["sub"] == "7"
    assert payload["session_token"] == "session-123"


def test_decode_rejects_token_signed_with_another_secret():
    token = jwt.encode(
        {"sub": "7", "exp": _expiry()},
        "otro-secreto-con-al-menos-32-caracteres!!",
        algorithm=settings.jwt_algorithm,
    )

    assert security.decode_jwt(token) is None


def test_decode_rejects_tampered_token():
    token = security.create_jwt("session-123", 7, _expiry())
    tampered = token[:-2] + ("aa" if not token.endswith("aa") else "bb")

    assert security.decode_jwt(tampered) is None

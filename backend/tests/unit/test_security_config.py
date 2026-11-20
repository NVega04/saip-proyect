"""Tests de la configuración de seguridad introducida en la Fase 2."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.core.config import Settings, settings

BACKEND_DIR = Path(__file__).resolve().parents[2]


def test_app_does_not_start_without_jwt_secret():
    env = os.environ.copy()
    env["JWT_SECRET"] = ""
    result = subprocess.run(
        [sys.executable, "-c", "import src.core.config"],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "jwt_secret" in result.stderr


def test_settings_require_jwt_secret(monkeypatch):
    monkeypatch.delenv("JWT_SECRET", raising=False)

    with pytest.raises(ValidationError, match="jwt_secret"):
        Settings(_env_file=None, frontend_url="http://localhost:5173")


def test_settings_reject_short_jwt_secret(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "demasiado-corto")

    with pytest.raises(ValidationError, match="al menos 32"):
        Settings(_env_file=None, frontend_url="http://localhost:5173")


def test_sqlalchemy_echo_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("SQLALCHEMY_ECHO", raising=False)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    config = Settings(
        _env_file=None,
        jwt_secret="test-jwt-secret-con-al-menos-32-caracteres",
        frontend_url="http://localhost:5173",
    )

    assert config.sqlalchemy_echo is False
    assert config.cors_origins == ["http://localhost:5173"]


def test_cors_origins_are_normalized(monkeypatch):
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "http://localhost:5173/, https://saip.lat/ , http://localhost:5173",
    )

    config = Settings(
        _env_file=None,
        jwt_secret="test-jwt-secret-con-al-menos-32-caracteres",
        frontend_url="http://localhost:5173",
    )

    assert config.cors_origins == [
        "http://localhost:5173",
        "https://saip.lat",
    ]


def test_cors_origins_reject_invalid_origin(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "exp://*")

    with pytest.raises(ValidationError, match="Origen CORS inválido"):
        Settings(
            _env_file=None,
            jwt_secret="test-jwt-secret-con-al-menos-32-caracteres",
            frontend_url="http://localhost:5173",
        )


def test_frontend_url_is_normalized_and_links_are_built_from_it(monkeypatch):
    monkeypatch.setenv("FRONTEND_URL", "https://saip.lat/")

    config = Settings(
        _env_file=None,
        jwt_secret="test-jwt-secret-con-al-menos-32-caracteres",
    )

    assert config.frontend_url == "https://saip.lat"
    assert config.frontend_link("/login") == "https://saip.lat/login"
    assert config.frontend_link("reset-password?token=abc") == (
        "https://saip.lat/reset-password?token=abc"
    )
    assert settings.frontend_link("login").startswith(settings.frontend_url)

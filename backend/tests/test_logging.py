"""Tests de logging estructurado y correlación por petición (Fase 6).

No tocan la base de datos salvo cuando usan el fixture ``client``
(healthcheck), que ya está aislado por la suite.
"""

import json
import logging

import pytest
from pydantic import ValidationError

from src.core.config import Settings
from src.core.logging import (
    REDACTED,
    JsonFormatter,
    RedactionFilter,
    request_id_var,
    redact,
    setup_logging,
)


def _record(msg: str, *args, level: int = logging.INFO) -> logging.LogRecord:
    return logging.LogRecord(
        name="src.prueba",
        level=level,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=args,
        exc_info=None,
    )


# ---------------------------------------------------------------- redacción


def test_redact_masks_password_and_token_values():
    text = "login password=SuperSecret123 token=abc123def"
    result = redact(text)

    assert "SuperSecret123" not in result
    assert "abc123def" not in result
    assert REDACTED in result


def test_redact_masks_jwt_anywhere_in_the_message():
    jwt = (
        "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0."
        "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJVadQssw5c"
    )
    result = redact(f"token extraído: {jwt}")

    assert jwt not in result
    assert REDACTED in result


def test_redact_masks_bearer_headers():
    result = redact("Authorization: Bearer sk-live-9999")

    assert "sk-live-9999" not in result
    assert REDACTED in result


def test_redaction_filter_cleans_the_record():
    record = _record("password=%s", "clave-secreta")

    assert RedactionFilter().filter(record) is True
    assert "clave-secreta" not in record.getMessage()
    assert record.args is None


def test_json_formatter_redacts_even_without_the_filter():
    formatter = JsonFormatter()
    payload = json.loads(formatter.format(_record("token=abcdef123456")))

    assert "abcdef123456" not in payload["message"]
    assert REDACTED in payload["message"]


def test_json_formatter_redacts_sensitive_extras():
    formatter = JsonFormatter()
    record = _record("ok")
    record.password = "no-deberia-verse"
    record.user_email = "persona@ejemplo.com"

    payload = json.loads(formatter.format(record))

    assert payload["extra"]["password"] == REDACTED
    # El resto de extras no sensibles se conservan.
    assert payload["extra"]["user_email"] == "persona@ejemplo.com"


# ------------------------------------------------------------ formato JSON


def test_json_formatter_emits_one_structured_line():
    payload = json.loads(JsonFormatter().format(_record("venta creada")))

    assert payload["message"] == "venta creada"
    assert payload["level"] == "INFO"
    assert payload["logger"] == "src.prueba"
    assert payload["request_id"] is None
    assert payload["timestamp"].endswith("+00:00")


def test_json_formatter_includes_the_request_id_from_context():
    token = request_id_var.set("abc-123")
    try:
        payload = json.loads(JsonFormatter().format(_record("hola")))
    finally:
        request_id_var.reset(token)

    assert payload["request_id"] == "abc-123"


def test_json_formatter_serializes_exception():
    try:
        raise ValueError("boom")
    except ValueError:
        import sys

        record = _record("falló")
        record.exc_info = sys.exc_info()

    payload = json.loads(JsonFormatter().format(record))

    assert "ValueError: boom" in payload["exception"]


# ---------------------------------------------------------- configuración


def test_setup_logging_is_idempotent_and_respects_the_level():
    root = logging.getLogger()
    managed_before = [
        h for h in root.handlers if getattr(h, "_saip_managed", False)
    ]

    setup_logging(level="DEBUG", fmt="json")
    setup_logging(level="WARNING", fmt="text")

    managed_after = [
        h for h in root.handlers if getattr(h, "_saip_managed", False)
    ]

    # Nunca se acumulan handlers.
    assert len(managed_after) == 1
    assert len(managed_before) <= 1
    assert root.level == logging.WARNING

    # Restaura el comportamiento por defecto para el resto de la suite.
    setup_logging(level="INFO", fmt="json")


def test_settings_reject_unknown_log_level():
    with pytest.raises(ValidationError):
        Settings(log_level="TRACE")


def test_settings_reject_unknown_log_format():
    with pytest.raises(ValidationError):
        Settings(log_format="xml")


def test_settings_normalize_level_and_format():
    settings = Settings(log_level="debug", log_format=" JSON ")

    assert settings.log_level == "DEBUG"
    assert settings.log_format == "json"


def test_setup_logging_integrates_the_uvicorn_loggers():
    setup_logging(level="INFO", fmt="json")

    access = logging.getLogger("uvicorn.access")
    error = logging.getLogger("uvicorn.error")

    # El access log de uvicorn se silencia (incluye la query string) y el
    # resto se integra en la salida estructurada del raíz.
    assert access.propagate is False
    assert access.level == logging.WARNING
    assert error.propagate is True
    assert not error.handlers


# ------------------------------------------------------ petición (middleware)


def test_response_carries_a_request_id_header(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers.get("x-request-id")


def test_incoming_request_id_is_echoed_back(client):
    response = client.get("/health", headers={"X-Request-ID": "front-42"})

    assert response.headers.get("x-request-id") == "front-42"


def test_access_log_carries_the_same_request_id_as_the_response(
    client, caplog
):
    caplog.set_level(logging.INFO, logger="src.core.middleware")

    # Ruta inexistente: el middleware la registra a INFO (no es healthcheck).
    response = client.get("/ruta-inexistente-para-logs")
    response_id = response.headers.get("x-request-id")

    access = [r for r in caplog.records if r.name == "src.core.middleware"]
    assert access, "no se registró la línea de acceso"
    assert "404" in access[-1].getMessage()

    # El registro formateado lleva el mismo ID que la cabecera de respuesta.
    payload = json.loads(JsonFormatter().format(access[-1]))
    assert payload["request_id"] == response_id
    assert payload["extra"]["http_status"] == 404

"""Logging estructurado de la aplicación (Fase 6).

Proporciona:

* ``setup_logging()``: configuración única que reemplaza el antiguo
  ``logging.basicConfig(level=WARNING)`` de ``main.py``. El nivel y el
  formato se leen de ``LOG_LEVEL`` y ``LOG_FORMAT`` (``core/config.py``).
* ``JsonFormatter``: cada registro es un objeto JSON en una línea, con
  ``timestamp`` UTC, ``level``, ``logger``, ``message`` y ``request_id``.
* ``RedactionFilter``: red de seguridad que enmascara valores sensibles
  (contraseñas, tokens, secretos) aparezcan donde aparezcan en el mensaje.
* ``request_id_var``: variable de contexto que el middleware de peticiones
  rellena para correlacionar todos los registros de una misma petición.

El envío a una plataforma centralizada (ELK/Datadog/Loki) es solo diseño:
ver ``docs/ARQUITECTURA.md``; no está implementado a propósito.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Optional

# Correlación de logs por petición; la rellena ``core/middleware.py``.
request_id_var: ContextVar[Optional[str]] = ContextVar(
    "request_id", default=None
)

REDACTED = "***"

# Claves cuyo valor jamás debe aparecer en un registro.
_SENSITIVE_KEY = re.compile(
    r"(?i)\b("
    r"password|passwd|pwd|new_password|old_password|"
    r"token|session[-_]?token|access[-_]?token|refresh[-_]?token|"
    r"secret|jwt[-_]?secret|api[-_]?key|authorization|mail[-_]?password"
    r")\b(\s*[=:]\s*)((?:bearer\s+)?[^\s,;'\"\\)]+)"
)

# Mismo criterio aplicado al *nombre* de un campo de ``extra``.
_SENSITIVE_NAME = re.compile(
    r"(?i)password|passwd|pwd|token|secret|api[-_]?key|authorization"
)

# Un JWT (header.payload.signature) aunque no vaya precedido de "token=".
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]{4,}")

# "Bearer <token>".
_BEARER = re.compile(r"(?i)\b(bearer\s+)([A-Za-z0-9._-]+)")

# Atributos estándar de LogRecord: todo lo demás se considera "extra".
# ``request_id`` se trata como campo propio del formato, no como extra.
_STANDARD_ATTRS = {
    "args", "asctime", "created", "exc_info", "exc_text", "filename",
    "funcName", "levelname", "levelno", "lineno", "message", "module",
    "msecs", "name", "msg", "pathname", "process", "processName",
    "relativeCreated", "request_id", "stack_info", "taskName", "thread",
    "threadName",
}


def redact(text: str) -> str:
    """Enmascara valores sensibles dentro de un texto libre."""
    text = _SENSITIVE_KEY.sub(
        lambda m: f"{m.group(1)}{m.group(2)}{REDACTED}", text
    )
    text = _BEARER.sub(lambda m: f"{m.group(1)}{REDACTED}", text)
    return _JWT.sub(REDACTED, text)


class RedactionFilter(logging.Filter):
    """Filtra valores sensibles del mensaje antes de formatearlo."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact(record.getMessage())
        record.args = None
        return True


class JsonFormatter(logging.Formatter):
    """Un objeto JSON por línea, listo para un colector centralizado."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": redact(record.getMessage()),
            # El middleware fija el ID en el propio registro; si no, se lee
            # del contexto (válido mientras la petición siga en curso).
            "request_id": getattr(record, "request_id", None)
            or request_id_var.get(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _STANDARD_ATTRS and not key.startswith("_")
        }
        if extras:
            payload["extra"] = {
                key: (
                    REDACTED
                    if _SENSITIVE_NAME.search(key)
                    else redact(value)
                    if isinstance(value, str)
                    else value
                )
                for key, value in extras.items()
            }

        return json.dumps(payload, ensure_ascii=False, default=str)


class TextFormatter(logging.Formatter):
    """Formato legible para consola en desarrollo (``LOG_FORMAT=text``)."""

    def format(self, record: logging.LogRecord) -> str:
        record.msg = redact(record.getMessage())
        record.args = None
        base = super().format(record)
        request_id = request_id_var.get()
        return f"{base} (request_id={request_id})" if request_id else base


def _build_formatter(fmt: str) -> logging.Formatter:
    if fmt == "json":
        return JsonFormatter()
    return TextFormatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _adopt_uvicorn_loggers(level: str) -> None:
    """Integra los loggers de uvicorn en la configuración central.

    * ``uvicorn`` / ``uvicorn.error`` (arranque, errores) → propagan al raíz
      para que salgan en el mismo formato estructurado.
    * ``uvicorn.access`` → se silencia: su línea incluye la query string, que
      puede contener datos personales. El ``RequestIdMiddleware`` ya registra
      el acceso (método, ruta, estado y duración) sin la query.
    """
    for name in ("uvicorn", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(name)
        for handler in list(uvicorn_logger.handlers):
            uvicorn_logger.removeHandler(handler)
        uvicorn_logger.propagate = True
        uvicorn_logger.setLevel(level)

    access_logger = logging.getLogger("uvicorn.access")
    for handler in list(access_logger.handlers):
        access_logger.removeHandler(handler)
    access_logger.propagate = False
    access_logger.setLevel(logging.WARNING)


def setup_logging(level: str = "INFO", fmt: str = "json") -> None:
    """Configura el logging raíz de forma idempotente.

    Solo toca los handlers creados por esta función, para no pisar los que
    pueda añadir ``caplog`` u otro instrumento de prueba.
    """
    root = logging.getLogger()
    root.setLevel(level)

    for handler in list(root.handlers):
        if getattr(handler, "_saip_managed", False):
            root.removeHandler(handler)
            handler.close()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(_build_formatter(fmt))
    handler.addFilter(RedactionFilter())
    handler._saip_managed = True  # type: ignore[attr-defined]
    root.addHandler(handler)

    _adopt_uvicorn_loggers(level)

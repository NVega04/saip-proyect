"""Middleware de correlación de peticiones (Fase 6).

Genera (o respeta) un ``X-Request-ID`` por petición, lo publica en la
variable de contexto ``core.logging.request_id_var`` para que todos los
registros de esa petición lo lleven, y lo devuelve en la cabecera de
respuesta para que el frontend pueda citarlo en un reporte de error.
"""

from __future__ import annotations

import logging
import time
from uuid import uuid4

from starlette.datastructures import Headers
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.core.logging import request_id_var

logger = logging.getLogger(__name__)

# Endpoint de monitorización: se registra a nivel DEBUG para no ensuciar
# los logs de producción con healthchecks.
_HEALTH_PATHS = {"/health"}


class RequestIdMiddleware:
    """ASGI puro (sin ``BaseHTTPMiddleware``) para no penalizar streaming."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        incoming = headers.get("x-request-id", "").strip()
        request_id = incoming[:64] if incoming else uuid4().hex
        token = request_id_var.set(request_id)

        path = scope.get("path", "")
        method = scope.get("method", "")
        started = time.perf_counter()
        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 500)
                raw = message.setdefault("headers", [])
                raw.append((b"x-request-id", request_id.encode("ascii", "ignore")))
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 1)
            # Sin query string: puede contener datos personales (búsquedas).
            log = logger.debug if path in _HEALTH_PATHS else logger.info
            log(
                "%s %s -> %s (%.1f ms)",
                method,
                path,
                status_code,
                duration_ms,
                extra={
                    "request_id": request_id,
                    "http_method": method,
                    "http_path": path,
                    "http_status": status_code,
                    "duration_ms": duration_ms,
                },
            )
            request_id_var.reset(token)

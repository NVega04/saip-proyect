"""Limitador de peticiones compartido por toda la aplicación."""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.core.config import settings


def client_ip(request: Request) -> str:
    """Devuelve la IP del cliente.

    ``X-Forwarded-For`` solo se tiene en cuenta cuando la petición llega desde
    un proxy declarado explícitamente en ``TRUSTED_PROXY_HOSTS``; en cualquier
    otro caso se usa la IP de la conexión para no permitir suplantación.
    """
    host = request.client.host if request.client else ""
    if host in settings.trusted_proxy_hosts:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(
    key_func=client_ip,
    default_limits=[settings.rate_limit_default],
)

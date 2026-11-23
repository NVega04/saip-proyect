"""Respuestas de error reutilizables para el contrato OpenAPI.

Los errores de dominio se traducen en ``{"detail": "..."}`` mediante el
handler de ``DomainError`` en ``main.py``; los de validación usan el esquema
``HTTPValidationError`` que genera FastAPI. Centralizar las descripciones y
los ejemplos evita que Swagger documente códigos genéricos ("Conflict",
"Gone") o que cada router repita el mismo bloque.

Uso::

    app.include_router(router, responses=AUTH_ERRORS)  # 401 global

    @router.post("/", responses={409: CONFLICT, 404: NOT_FOUND})
    def create(...): ...

Las respuestas declaradas en el ``@router.*`` ganan sobre las del
``include_router`` (verificado con FastAPI 0.115).
"""

from typing import Any

_ERROR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"detail": {"type": "string"}},
    "required": ["detail"],
}


def error(description: str, detail: str) -> dict[str, Any]:
    """Construye una respuesta de error con el mismo formato que la API."""
    return {
        "description": description,
        "content": {
            "application/json": {
                "schema": _ERROR_SCHEMA,
                "example": {"detail": detail},
            }
        },
    }


UNAUTHORIZED = error(
    "Falta el header session-token, o la sesión es inválida o expirada.",
    "Token inválido",
)
FORBIDDEN = error(
    "El usuario no tiene permisos para esta operación.",
    "No tienes acceso al módulo 'sales'.",
)
BAD_REQUEST = error(
    "No se cumple una regla de negocio (stock, estado, ventana de tiempo, etc.).",
    "No se cumple una regla de negocio.",
)
STOCK_ERROR = error(
    "Stock insuficiente para uno de los artículos de la operación.",
    "Stock insuficiente para 'Pan de yuca': disponible 3, solicitado 10.",
)
NOT_FOUND = error(
    "No existe el recurso solicitado o está eliminado lógicamente.",
    "Recurso no encontrado",
)
CONFLICT = error(
    "El recurso ya existe o su estado no permite la operación.",
    "El email 'admin@saip.com' ya está registrado.",
)
CONFLICT_STATE = error(
    "El estado actual del recurso no permite la transición solicitada.",
    "Solo se pueden completar órdenes en estado 'in_progress'.",
)
GONE = error(
    "El recurso está desactivado; debe reactivarse antes de modificarse.",
    "El rol ya esta desactivado",
)
LOCKED = error(
    "La cuenta fue bloqueada temporalmente por intentos fallidos.",
    "Cuenta bloqueada temporalmente por intentos fallidos.",
)
RATE_LIMITED = error(
    "Demasiadas peticiones en la ventana de tiempo permitida.",
    "Rate limit exceeded: 5 per 1 minute",
)

#: Se aplica a todos los routers autenticados desde ``main.py``.
AUTH_ERRORS: dict[int | str, dict[str, Any]] = {401: UNAUTHORIZED}

#: Errores habituales del flujo de autenticación (se declaran por ruta).
AUTH_FLOW_ERRORS: dict[int | str, dict[str, Any]] = {
    403: FORBIDDEN,
    423: LOCKED,
    429: RATE_LIMITED,
}

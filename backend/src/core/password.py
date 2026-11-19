"""Política de contraseñas del backend.

Los criterios y los mensajes son los mismos que usa el frontend en
``passwordStrength.ts`` para que ambos lados den exactamente el mismo
feedback al usuario.
"""

import re

from src.core.exceptions import BusinessRuleError

MIN_PASSWORD_LENGTH = 12

PASSWORD_HINTS = (
    "Mínimo 12 caracteres",
    "Al menos una mayúscula",
    "Al menos una minúscula",
    "Al menos un número",
    "Al menos un carácter especial",
)


def password_errors(password: str) -> list[str]:
    """Devuelve los criterios incumplidos, en el mismo orden que el frontend."""
    errors: list[str] = []
    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(PASSWORD_HINTS[0])
    if not re.search(r"[A-Z]", password):
        errors.append(PASSWORD_HINTS[1])
    if not re.search(r"[a-z]", password):
        errors.append(PASSWORD_HINTS[2])
    if not re.search(r"[0-9]", password):
        errors.append(PASSWORD_HINTS[3])
    if not re.search(r"[^A-Za-z0-9]", password):
        errors.append(PASSWORD_HINTS[4])
    return errors


def validate_password(password: str) -> str:
    """Lanza ``BusinessRuleError`` (400) si la contraseña es débil."""
    errors = password_errors(password)
    if errors:
        raise BusinessRuleError(
            "La contraseña no cumple la política: " + "; ".join(errors) + "."
        )
    return password

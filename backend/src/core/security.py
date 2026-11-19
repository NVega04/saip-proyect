import secrets
import string
import uuid
from datetime import datetime, timedelta

import bcrypt
import jwt

from src.core.config import settings
from src.core.password import password_errors
from src.core.time import BOGOTA_TZ

# Sin valor por defecto: ``Settings.jwt_secret`` es obligatorio y la
# importación falla si JWT_SECRET no está configurado (ver src.core.config).
JWT_SECRET = settings.jwt_secret
JWT_ALGORITHM = settings.jwt_algorithm

# Definición de duración de la sesión del usuario en horas
SESSION_DURATION_HOURS = settings.session_duration_hours


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except (ValueError, TypeError):
        # Hash inválido o malformado: tratar como credencial incorrecta
        return False


TEMP_PASSWORD_ALPHABET = string.ascii_letters + string.digits + "!@#$%^*-_?"
TEMP_PASSWORD_LENGTH = 14


def generate_temp_password() -> str:
    """Genera una contraseña temporal que cumple la política de la Fase 2.

    Se generan caracteres de todas las clases requeridas y se repite el
    proceso hasta que el validador compartido no reporte errores. El valor
    nunca se escribe en logs: solo se envía por correo al usuario.
    """
    while True:
        candidate = "".join(
            secrets.choice(TEMP_PASSWORD_ALPHABET)
            for _ in range(TEMP_PASSWORD_LENGTH)
        )
        if not password_errors(candidate):
            return candidate


def create_session_token() -> str:
    return str(uuid.uuid4())


def get_session_expiry() -> datetime:
    return datetime.now(BOGOTA_TZ) + timedelta(hours=SESSION_DURATION_HOURS)


def create_jwt(session_token: str, user_id: int, expires_at: datetime) -> str:
    payload = {
        "sub": str(user_id),
        "session_token": session_token,
        "exp": expires_at,
        "iat": datetime.now(BOGOTA_TZ),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None

import bcrypt
import secrets
import string
import os
import jwt
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

BOGOTA_TZ = ZoneInfo("America/Bogota")

JWT_SECRET = os.getenv("JWT_SECRET", "cambiar-en-produccion")
JWT_ALGORITHM = "HS256"

#Definición de duración de la sessión del usuario en horas
SESSION_DURATION_HOURS = 8

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def generate_temp_password() -> str:
    """
    Genera una password temporal legible.
    Formato: Temp@ + 4 dígitos + 2 letras mayúsculas
    Ejemplo: Temp@4821XK
    """
    digits = ''.join(secrets.choice(string.digits) for _ in range(4))
    letters = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(2))
    return f"Temp@{digits}{letters}"

def create_session_token() -> str:
    import uuid
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
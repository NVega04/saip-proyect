import bcrypt
import secrets
import string
from datetime import datetime, timezone, timedelta

#Definición de duración de la sessión del usuario en horas
SESSION_DURATION_HOURS = 1

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
    return datetime.now(timezone.utc) + timedelta(hours=SESSION_DURATION_HOURS)
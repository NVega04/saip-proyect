from passlib.context import CryptContext
import secrets
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def generate_temp_password() -> str:
    """
    Genera una password temporal legible.
    Formato: Temp@ + 4 dígitos + 2 letras mayúsculas
    Ejemplo: Temp@4821XK
    """
    digits = ''.join(secrets.choice(string.digits) for _ in range(4))
    letters = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(2))
    return f"Temp@{digits}{letters}"

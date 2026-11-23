"""Cifrado de campos sensibles e índice ciego para búsquedas.

``ENCRYPTION_KEY`` admite varias claves Fernet separadas por comas: la primera
cifra los valores nuevos y todas descifran, lo que permite rotar sin perder
lectura de los datos antiguos.
"""

import base64
import hashlib
import hmac
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from sqlalchemy.types import String, TypeDecorator

from src.core.config import settings


def _build_fernet() -> MultiFernet:
    keys = [key.strip() for key in settings.encryption_key.split(",") if key.strip()]
    return MultiFernet([Fernet(key.encode()) for key in keys])


fernet = _build_fernet()


def blind_index(value: str) -> str:
    """HMAC determinista y irreversible para comparar NIT sin descifrar."""
    active_key = settings.encryption_key.split(",")[0].strip()
    raw_key = base64.urlsafe_b64decode(active_key)
    normalized = "".join(ch for ch in value.upper() if ch.isalnum()).encode()
    return hmac.new(raw_key, normalized, hashlib.sha256).hexdigest()


class EncryptedString(TypeDecorator):
    """Columna que almacena texto cifrado y lo expone en claro al modelo."""

    impl = String
    cache_ok = True

    def __init__(self, length: int = 255):
        super().__init__(length=length)

    def process_bind_param(self, value, dialect) -> Optional[str]:  # noqa: ANN001
        if value is None:
            return None
        return fernet.encrypt(str(value).encode()).decode()

    def process_result_value(self, value, dialect) -> Optional[str]:  # noqa: ANN001
        if value is None:
            return None
        try:
            return fernet.decrypt(value.encode()).decode()
        except InvalidToken:
            # Durante la migración puede quedar texto plano legacy.
            return value

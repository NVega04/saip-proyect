"""Configuración centralizada de la aplicación.

Los valores de seguridad son obligatorios o tienen valores seguros por defecto:
``JWT_SECRET`` y ``FRONTEND_URL`` deben venir del entorno, ``SQLALCHEMY_ECHO``
está desactivado y ``CORS_ORIGINS`` se lee como lista separada por comas.
El logging se configura con ``LOG_LEVEL`` (``INFO`` por defecto) y
``LOG_FORMAT`` (``json`` por defecto, o ``text`` para consola legible).
"""

from typing import Annotated, Optional

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
    )

    # Base de datos
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    db_host: Optional[str] = None
    db_port: Optional[str] = None
    db_name: Optional[str] = None
    sqlalchemy_echo: bool = False

    # Seguridad / sesiones
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    session_duration_hours: int = 8

    # Orígenes permitidos por CORS (CSV en la variable de entorno)
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    # Correo
    mail_host: Optional[str] = None
    mail_port: int = 587
    mail_username: Optional[str] = None
    mail_password: Optional[str] = None
    mail_from: Optional[str] = None

    # Frontend
    frontend_url: str

    # Logging (Fase 6): nivel y formato por entorno
    log_level: str = "INFO"
    log_format: str = "json"

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, value: str) -> str:
        secret = value.strip()
        if len(secret) < 32:
            raise ValueError("JWT_SECRET debe tener al menos 32 caracteres.")
        return secret

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            value = value.split(",")
        origins = [
            str(origin).strip().rstrip("/")
            for origin in value
            if str(origin).strip()
        ]
        if not origins:
            raise ValueError("CORS_ORIGINS debe contener al menos un origen.")
        for origin in origins:
            if (
                "*" in origin
                or not origin.startswith(("http://", "https://"))
            ):
                raise ValueError(f"Origen CORS inválido: {origin!r}")
        return list(dict.fromkeys(origins))

    @field_validator("frontend_url")
    @classmethod
    def validate_frontend_url(cls, value: str) -> str:
        url = value.strip().rstrip("/")
        if not url.startswith(("http://", "https://")):
            raise ValueError("FRONTEND_URL debe ser una URL http:// o https://")
        return url

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        level = value.strip().upper()
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if level not in allowed:
            raise ValueError(
                f"LOG_LEVEL debe ser uno de: {', '.join(sorted(allowed))}."
            )
        return level

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, value: str) -> str:
        fmt = value.strip().lower()
        if fmt not in {"json", "text"}:
            raise ValueError("LOG_FORMAT debe ser 'json' o 'text'.")
        return fmt

    @property
    def mysql_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def frontend_link(self, path: str) -> str:
        """Construye un enlace al frontend sin duplicar barras ni hardcodearlo."""
        return f"{self.frontend_url}/{path.lstrip('/')}"


settings = Settings()

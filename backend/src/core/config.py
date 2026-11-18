"""Configuración centralizada de la aplicación.

En esta fase solo se centraliza la lectura de variables de entorno; los valores
por defecto se mantienen idénticos a los que tenía el código previo. El
endurecimiento de valores obligatorios corresponde a la Fase 2.
"""

from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

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
    sqlalchemy_echo: bool = True

    # Seguridad / sesiones
    jwt_secret: str = "cambiar-en-produccion"
    jwt_algorithm: str = "HS256"
    session_duration_hours: int = 8

    # Correo
    mail_host: Optional[str] = None
    mail_port: int = 587
    mail_username: Optional[str] = None
    mail_password: Optional[str] = None
    mail_from: Optional[str] = None

    # Frontend
    frontend_url: Optional[str] = None

    @property
    def mysql_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()

"""Configuración base de la suite de pruebas de SAIP.

Reglas de esta Fase 0:

* Las pruebas **nunca** tocan la base de datos de desarrollo ni el archivo
  ``.env``. Se usa una base separada (``db_saip_test`` por defecto) construida
  a partir de las mismas credenciales, reemplazando solo el nombre de la base.
* El esquema se crea con ``SQLModel.metadata`` (no con migraciones) y se
  recrea una vez por sesión de pytest.
* Cada test corre dentro de una transacción externa que se revierte al final,
  de modo que los ``commit()`` de los servicios no dejan rastro.
* Los limitadores de peticiones y los envíos de correo se desactivan.
"""

import os
import re
from uuid import uuid4

import pytest

# Debe definirse antes de importar ``src.*``: ``src.core.config`` lee el
# entorno al importarse. ``setdefault`` garantiza que no se pisa una variable
# ya definida por el entorno de CI.
os.environ.setdefault("TEST_DB_NAME", "db_saip_test")
# La Fase 2 exige estas variables. Valores falsos y deterministas para la
# suite; nunca se lee ni se modifica el ``.env`` real.
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-con-al-menos-32-caracteres")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")
# Fase 3: claves Fernet falsas, usadas solo por la suite. La segunda permite
# probar la rotación sin tocar el ``.env`` real ni secretos de despliegue.
os.environ.setdefault(
    "ENCRYPTION_KEY",
    "smtkqsJHxX01CFiTpIHWcIZXrEpMvub2Mm1TIcdme-Y=,"
    "Nar9iorIwAUBeSVgqETB2ei86pd5a09hV2wl93FGAdk=",
)

import pymysql  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

import src.models_registry  # noqa: E402,F401  (registra las 22 tablas)
from src.core.config import settings  # noqa: E402
from src.core.database import get_session  # noqa: E402
from src.core.security import create_jwt, get_session_expiry, hash_password  # noqa: E402
from src.main import app  # noqa: E402
from src.modules.roles.models import Role, RoleStatus  # noqa: E402
from src.modules.users.models import SessionApp, User, UserStatus  # noqa: E402

TEST_DB_NAME = os.environ["TEST_DB_NAME"]
TEST_USER_PASSWORD = "Prueba123!"

_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9_]+$")


def _assert_safe_test_database() -> None:
    """Impide apuntar por error a la base de desarrollo."""
    if not _SAFE_IDENTIFIER.match(TEST_DB_NAME):
        raise RuntimeError(
            f"TEST_DB_NAME={TEST_DB_NAME!r} no es un nombre de base válido."
        )
    if not TEST_DB_NAME.endswith("_test"):
        raise RuntimeError(
            f"TEST_DB_NAME={TEST_DB_NAME!r} debe terminar en '_test' para evitar "
            "borrar datos reales."
        )
    if TEST_DB_NAME == settings.db_name:
        raise RuntimeError(
            f"TEST_DB_NAME={TEST_DB_NAME!r} es igual a DB_NAME; las pruebas "
            "borrarían la base de desarrollo."
        )


def _database_url(database: str = "") -> str:
    return (
        f"mysql+pymysql://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{database}"
    )


def _ensure_database_exists() -> None:
    connection = pymysql.connect(
        host=settings.db_host,
        port=int(settings.db_port or 3306),
        user=settings.db_user,
        password=settings.db_password,
        charset="utf8mb4",
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{TEST_DB_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        connection.commit()
    finally:
        connection.close()


@pytest.fixture(scope="session")
def engine():
    """Engine de la base de test, con el esquema recreado una sola vez."""
    _assert_safe_test_database()
    _ensure_database_exists()

    test_engine = create_engine(_database_url(TEST_DB_NAME), echo=False)

    # El esquema se reconstruye desde la metadata actual para que las pruebas
    # siempre vean el modelo vigente. Se desactivan las FKs porque ``users`` y
    # ``roles`` se referencian mutuamente.
    with test_engine.begin() as connection:
        connection.exec_driver_sql("SET FOREIGN_KEY_CHECKS=0")
        try:
            SQLModel.metadata.drop_all(connection)
        finally:
            connection.exec_driver_sql("SET FOREIGN_KEY_CHECKS=1")
    SQLModel.metadata.create_all(test_engine)

    yield test_engine
    test_engine.dispose()


@pytest.fixture()
def db_connection(engine):
    """Conexión con una transacción externa que se revierte por test."""
    connection = engine.connect()
    transaction = connection.begin()
    try:
        yield connection
    finally:
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture()
def db_session(db_connection):
    """Sesión ORM aislada por test.

    ``join_transaction_mode="create_savepoint"`` permite que los ``commit()``
    de los servicios se conviertan en savepoints, de modo que el rollback de
    ``db_connection`` deshace todo lo escrito durante la prueba.
    """
    session = Session(bind=db_connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """``TestClient`` con ``get_session`` apuntando a la sesión de test."""

    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def disable_rate_limits(monkeypatch):
    """Desactiva el limitador global; sus regresiones se prueban por separado."""
    import src.core.rate_limit as rate_limit_module

    monkeypatch.setattr(rate_limit_module.limiter, "enabled", False, raising=False)


@pytest.fixture(autouse=True)
def block_outgoing_email(monkeypatch):
    """Evita que las pruebas intenten abrir conexiones SMTP reales."""
    from src.modules.auth import service as auth_service
    from src.modules.users import service as users_service

    monkeypatch.setattr(auth_service, "send_reset_email", lambda *a, **k: None)
    monkeypatch.setattr(users_service, "send_welcome_email", lambda *a, **k: None)
    monkeypatch.setattr(
        users_service, "send_deactivation_email", lambda *a, **k: None
    )


def _unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}@saip.com"


def _make_role(session: Session) -> Role:
    role = Role(
        name=f"Rol prueba {uuid4().hex[:8]}",
        description="Rol creado por la suite de pruebas",
        status=RoleStatus.ACTIVE,
    )
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


def _make_user(
    session: Session, role: Role, *, is_admin: bool, prefix: str
) -> User:
    user = User(
        first_name="Usuario",
        last_name="Pruebas",
        email=_unique_email(prefix),
        password_hash=hash_password(TEST_USER_PASSWORD),
        role_id=role.id,
        is_admin=is_admin,
        status=UserStatus.ACTIVE,
        accepted_terms=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _make_session_token(session: Session, user: User) -> str:
    user_session = SessionApp(user_id=user.id, expires_at=get_session_expiry())
    session.add(user_session)
    session.commit()
    session.refresh(user_session)
    return create_jwt(user_session.token, user.id, user_session.expires_at)


@pytest.fixture()
def admin_role(db_session):
    return _make_role(db_session)


@pytest.fixture()
def admin_user(db_session, admin_role):
    return _make_user(db_session, admin_role, is_admin=True, prefix="admin")


@pytest.fixture()
def admin_headers(db_session, admin_user):
    return {"session-token": _make_session_token(db_session, admin_user)}


@pytest.fixture()
def limited_role(db_session):
    """Rol sin módulos asignados: no puede pasar ``require_module``."""
    return _make_role(db_session)


@pytest.fixture()
def limited_user(db_session, limited_role):
    return _make_user(db_session, limited_role, is_admin=False, prefix="limited")


@pytest.fixture()
def limited_headers(db_session, limited_user):
    return {"session-token": _make_session_token(db_session, limited_user)}

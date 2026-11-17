"""Comprobaciones básicas de la base de datos de pruebas y del cliente HTTP."""

import os

from sqlmodel import select

from src.core.config import settings
from src.modules.units.models import Unit

TEST_DB_NAME = os.environ.get("TEST_DB_NAME", "db_saip_test")


def test_database_in_use_is_the_test_database(engine):
    with engine.connect() as connection:
        database = connection.exec_driver_sql("SELECT DATABASE()").scalar()

    assert database == TEST_DB_NAME
    assert database.endswith("_test")
    assert database != settings.db_name


def test_writes_are_not_visible_outside_the_test_transaction(db_session, engine):
    unit = Unit(name="unidad-aislamiento", abbreviation="uai", description="prueba")
    db_session.add(unit)
    db_session.commit()
    db_session.refresh(unit)

    assert unit.id is not None

    # Otra conexión no debe ver la fila: sigue dentro de la transacción que se
    # revertirá al terminar el test.
    with engine.connect() as connection:
        count = connection.exec_driver_sql(
            "SELECT COUNT(*) FROM units WHERE name = 'unidad-aislamiento'"
        ).scalar()

    assert count == 0


def test_health_endpoint_uses_test_session(client, db_session):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    stored = db_session.exec(select(Unit)).all()
    assert stored == []

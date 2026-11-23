"""Regresiones del cifrado de NIT y teléfonos de la Fase 3."""

from cryptography.fernet import Fernet
from sqlalchemy import text

from src.core.crypto import EncryptedString, blind_index, fernet
from src.modules.providers.models import Provider
from src.modules.users.models import User


def test_encrypted_string_round_trip():
    column = EncryptedString(255)
    stored = column.process_bind_param("900123456", None)

    assert stored != "900123456"
    assert column.process_result_value(stored, None) == "900123456"
    assert column.process_result_value(None, None) is None


def test_blind_index_is_deterministic_and_normalized():
    assert blind_index("900.123.456-7") == blind_index("9001234567")
    assert blind_index("900123456") != blind_index("900123457")


def test_rotation_decrypts_values_written_with_the_previous_key():
    previous_key = "Nar9iorIwAUBeSVgqETB2ei86pd5a09hV2wl93FGAdk="
    legacy_ciphertext = Fernet(previous_key.encode()).encrypt(b"3001234567")

    assert fernet.decrypt(legacy_ciphertext) == b"3001234567"


def test_provider_calculates_its_blind_index(db_session):
    provider = Provider(company="Panadería", nit="900123456", email="a@saip.com")
    db_session.add(provider)
    db_session.flush()
    assert provider.nit_hash == blind_index("900123456")


def test_nit_is_stored_encrypted(db_session):
    provider = Provider(company="Panadería", nit="900123456", email="b@saip.com")
    db_session.add(provider)
    db_session.flush()

    raw = db_session.exec(
        text("SELECT nit FROM providers WHERE id = :id"), params={"id": provider.id}
    ).one()
    assert raw != "900123456"
    assert provider.nit == "900123456"


def test_user_phone_is_encrypted_at_bind_time():
    user = User(
        first_name="Ana",
        last_name="Pérez",
        email="ana@saip.com",
        phone="3001234567",
        role_id=1,
        password_hash="hash",
    )
    assert user.phone == "3001234567"

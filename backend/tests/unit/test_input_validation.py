"""Regresiones de los límites de validación de la Fase 3."""

import pytest
from pydantic import ValidationError

from src.modules.audit.service import sanitize_audit_value
from src.modules.products.schemas import ProductCreate
from src.modules.providers.schemas import ProviderCreate


@pytest.mark.unit
def test_product_name_respects_database_length():
    with pytest.raises(ValidationError):
        ProductCreate(name="x" * 151, unit_id=1)


@pytest.mark.unit
def test_negative_foreign_keys_are_rejected():
    with pytest.raises(ValidationError):
        ProductCreate(name="Pan", unit_id=-1)


@pytest.mark.unit
def test_provider_nit_respects_database_length():
    with pytest.raises(ValidationError):
        ProviderCreate(company="Panadería", nit="1" * 21, email="a@saip.com")


@pytest.mark.unit
def test_audit_log_never_contains_nit_or_phone():
    value = {
        "company": "Panadería",
        "nit": "900123456",
        "phone": "600000000",
        "telefono": "601000000",
        "contact": {"celular": "602000000", "name": "Ana"},
    }
    assert sanitize_audit_value(value) == {
        "company": "Panadería",
        "contact": {"name": "Ana"},
    }

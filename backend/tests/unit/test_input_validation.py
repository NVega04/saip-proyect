"""Regresiones de los límites de validación de la Fase 3.

Los límites viven en la capa de servicios (``src.core.validation``) para no
modificar el OpenAPI aprobado en Fase 6.
"""

import pytest

from src.core.exceptions import UnprocessableError
from src.core.validation import validate_input
from src.modules.audit.service import sanitize_audit_value
from src.modules.products.schemas import ProductCreate
from src.modules.providers.schemas import ProviderCreate


@pytest.mark.unit
def test_product_name_respects_database_length():
    with pytest.raises(UnprocessableError, match="name"):
        validate_input(ProductCreate(name="x" * 151, unit_id=1), "ProductCreate")


@pytest.mark.unit
def test_negative_foreign_keys_are_rejected():
    with pytest.raises(UnprocessableError, match="unit_id"):
        validate_input(ProductCreate(name="Pan", unit_id=-1), "ProductCreate")


@pytest.mark.unit
def test_provider_nit_respects_database_length():
    provider = ProviderCreate(company="Panadería", nit="1" * 21, email="a@saip.com")
    with pytest.raises(UnprocessableError, match="nit"):
        validate_input(provider, "ProviderCreate")


@pytest.mark.unit
def test_service_validation_is_wired_into_the_api(client, admin_headers):
    response = client.post(
        "/products/",
        headers=admin_headers,
        json={"name": "Pan", "unit_id": -1},
    )
    assert response.status_code == 422, response.text
    assert "unit_id" in response.json()["detail"]


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

import pytest
from pydantic import ValidationError

from src.core.password import password_errors
from src.modules.sales.schemas import SaleAnnulRequest

pytestmark = pytest.mark.validation


def test_password_length_boundary_is_enforced():
    assert password_errors("Panaderia12!") == []
    assert "Mínimo 12 caracteres" in password_errors("Panaderia1!")


def test_sale_annulment_reason_enforces_length_bounds():
    with pytest.raises(ValidationError):
        SaleAnnulRequest(reason="ab")

    with pytest.raises(ValidationError):
        SaleAnnulRequest(reason="a" * 501)

    assert SaleAnnulRequest(reason="abc").reason == "abc"

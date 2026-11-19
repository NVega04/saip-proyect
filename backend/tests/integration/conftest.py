from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def unit(client: TestClient, admin_headers: dict[str, str]) -> dict:
    response = client.post(
        "/units/",
        json={
            "name": f"Unión auditoría {uuid4().hex[:8]}",
            "abbreviation": uuid4().hex[:8],
            "description": "unidad de prueba",
            "quantity": 1,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture()
def product(
    client: TestClient, admin_headers: dict[str, str], unit: dict
) -> dict:
    response = client.post(
        "/products/",
        json={
            "name": f"Producto auditoría {uuid4().hex[:8]}",
            "description": "producto de prueba",
            "unit_id": unit["id"],
            "available_quantity": 50,
            "min_stock": 5,
            "max_stock": 100,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture()
def sale(
    client: TestClient, admin_headers: dict[str, str], product: dict
) -> dict:
    response = client.post(
        "/sales/",
        json={
            "items": [
                {"item_type": "product", "item_id": product["id"], "quantity": 2}
            ],
            "notes": "venta para auditoría",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["sale"]

from uuid import uuid4

import pytest

from tests.conftest import TEST_USER_PASSWORD

pytestmark = pytest.mark.e2e


def test_login_sale_annulment_report_flow(client, admin_user):
    login = client.post(
        "/session/login",
        json={"email": admin_user.email, "password": TEST_USER_PASSWORD},
    )
    assert login.status_code == 200
    headers = {"session-token": login.json()["session_token"]}

    unit = client.post(
        "/units/",
        json={
            "name": f"Unidad E2E {uuid4().hex[:8]}",
            "abbreviation": uuid4().hex[:8],
            "description": "unidad del flujo e2e",
            "quantity": 1,
        },
        headers=headers,
    )
    assert unit.status_code == 201

    product = client.post(
        "/products/",
        json={
            "name": f"Producto E2E {uuid4().hex[:8]}",
            "description": "producto del flujo e2e",
            "unit_id": unit.json()["id"],
            "available_quantity": 20,
            "min_stock": 2,
            "max_stock": 50,
        },
        headers=headers,
    )
    assert product.status_code == 201

    sale = client.post(
        "/sales/",
        json={
            "items": [
                {
                    "item_type": "product",
                    "item_id": product.json()["id"],
                    "quantity": 2,
                }
            ],
            "notes": "venta del flujo e2e",
        },
        headers=headers,
    )
    assert sale.status_code == 201
    sale_id = sale.json()["sale"]["id"]

    detail = client.get(f"/sales/{sale_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["status"] == "completada"

    annulment = client.patch(
        f"/sales/{sale_id}/annul",
        json={"reason": "Prueba end-to-end de anulación"},
        headers=headers,
    )
    assert annulment.status_code == 200
    assert annulment.json()["status"] == "anulada"

    detail = client.get(f"/sales/{sale_id}", headers=headers)
    assert detail.json()["status"] == "anulada"

    report = client.get("/reports/products", headers=headers, params={"format": "json"})
    assert report.status_code == 200

    audit = client.get(
        "/audit/", headers=headers, params={"action": "sale.annulled"}
    )
    assert audit.status_code == 200
    assert audit.json()["total"] >= 1

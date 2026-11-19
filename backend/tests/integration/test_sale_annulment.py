from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session

from src.core.time import BOGOTA_TZ
from src.modules.sales.models import Sale


def _audit_rows(
    client: TestClient, admin_headers: dict[str, str], action: str
) -> list[dict]:
    response = client.get(
        "/audit/", headers=admin_headers, params={"action": action}
    )
    assert response.status_code == 200, response.text
    return response.json()["items"]


def test_annul_requires_module_and_reason(
    client: TestClient,
    admin_headers: dict[str, str],
    limited_headers: dict[str, str],
    sale: dict,
) -> None:
    sale_id = sale["id"]

    denied = client.patch(
        f"/sales/{sale_id}/annul",
        headers=limited_headers,
        json={"reason": "Sin módulo"},
    )
    assert denied.status_code == 403

    missing_reason = client.patch(
        f"/sales/{sale_id}/annul", headers=admin_headers, json={}
    )
    assert missing_reason.status_code == 422

    short_reason = client.patch(
        f"/sales/{sale_id}/annul", headers=admin_headers, json={"reason": "x"}
    )
    assert short_reason.status_code == 422

    annulled = client.patch(
        f"/sales/{sale_id}/annul",
        headers=admin_headers,
        json={"reason": "Error registrado en el pedido"},
    )
    assert annulled.status_code == 200, annulled.text
    assert annulled.json()["status"] == "anulada"

    again = client.patch(
        f"/sales/{sale_id}/annul",
        headers=admin_headers,
        json={"reason": "Segunda anulación"},
    )
    assert again.status_code == 400
    assert "Transición no permitida" in again.json()["detail"]


def test_annul_outside_window_keeps_stock_and_does_not_audit_success(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
    product: dict,
    sale: dict,
) -> None:
    sale_id = sale["id"]
    persisted = db_session.get(Sale, sale_id)
    assert persisted is not None
    persisted.sale_date = datetime.now(BOGOTA_TZ) - timedelta(hours=25)
    db_session.commit()

    response = client.patch(
        f"/sales/{sale_id}/annul",
        headers=admin_headers,
        json={"reason": "Fuera de plazo"},
    )
    assert response.status_code == 400
    assert "24 horas" in response.json()["detail"]

    after = client.get(f"/products/{product['id']}")
    assert after.json()["available_quantity"] == 48

    assert not _audit_rows(client, admin_headers, "sale.annulled")


def test_annul_audits_reason_and_inventory_movements(
    client: TestClient,
    admin_headers: dict[str, str],
    admin_user,
    sale: dict,
) -> None:
    sale_id = sale["id"]
    reason = "Producto dañado al entregar"

    response = client.patch(
        f"/sales/{sale_id}/annul",
        headers=admin_headers,
        json={"reason": reason},
    )
    assert response.status_code == 200, response.text

    sale_rows = _audit_rows(client, admin_headers, "sale.annulled")
    assert len(sale_rows) == 1
    assert sale_rows[0]["resource_id"] == sale_id
    assert sale_rows[0]["user_id"] == admin_user.id
    assert sale_rows[0]["old_value"]["status"] == "completada"
    assert sale_rows[0]["new_value"]["status"] == "anulada"
    assert sale_rows[0]["new_value"]["reason"] == reason

    movement_rows = _audit_rows(client, admin_headers, "inventory.movement_created")
    assert any(
        row["new_value"]["reference_id"] == sale_id
        and row["new_value"]["movement_type"] == "sale_annulment"
        for row in movement_rows
    )

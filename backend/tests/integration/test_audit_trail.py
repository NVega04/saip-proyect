from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session

from src.modules.audit.models import AuditLog
from src.modules.roles.models import Module


def _audit_rows(
    client: TestClient, admin_headers: dict[str, str], action: str
) -> list[dict]:
    response = client.get(
        "/audit/", headers=admin_headers, params={"action": action}
    )
    assert response.status_code == 200, response.text
    return response.json()["items"]


def test_audit_endpoint_is_admin_only(
    client: TestClient, limited_headers: dict[str, str]
) -> None:
    assert client.get("/audit/", headers=limited_headers).status_code == 403


def test_audit_endpoint_filters_and_redacts_secrets(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    entry = AuditLog(
        user_id=None,
        action="test.sensitive",
        resource_type="test",
        new_value={
            "email": "visible@saip.com",
            "password": "super-secreto",
            "access_token": "token-secreto",
            "nested": {"api_secret": "otro-secreto", "safe": "ok"},
        },
        ip_address="203.0.113.7",
    )
    db_session.add(entry)
    db_session.commit()

    rows = _audit_rows(client, admin_headers, "test.sensitive")

    assert len(rows) == 1
    row = rows[0]
    assert row["user_id"] is None
    assert row["ip_address"] == "203.0.113.7"
    assert row["new_value"]["email"] == "visible@saip.com"
    assert "password" not in row["new_value"]
    assert "access_token" not in row["new_value"]
    assert "api_secret" not in row["new_value"]["nested"]
    assert row["new_value"]["nested"]["safe"] == "ok"


def test_admin_user_creation_is_audited_with_actor(
    client: TestClient,
    admin_headers: dict[str, str],
    admin_user,
    limited_role,
) -> None:
    email = f"audit-{uuid4().hex[:10]}@saip.com"
    created = client.post(
        "/users/",
        json={
            "first_name": "Auditoría",
            "last_name": "Administrada",
            "email": email,
            "role_id": limited_role.id,
            "is_admin": False,
        },
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text

    rows = _audit_rows(client, admin_headers, "user.created")

    assert any(
        row["user_id"] == admin_user.id
        and row["new_value"]["email"] == email
        and "password" not in row["new_value"]
        for row in rows
    )


def test_role_modules_assignment_is_audited(
    client: TestClient,
    admin_headers: dict[str, str],
    admin_user,
    db_session: Session,
) -> None:
    modules = [
        Module(name=f"mod-audit-{uuid4().hex[:8]}", label="Módulo auditoría A"),
        Module(name=f"mod-audit-{uuid4().hex[:8]}", label="Módulo auditoría B"),
    ]
    db_session.add_all(modules)
    db_session.commit()
    for module in modules:
        db_session.refresh(module)
    module_ids = [module.id for module in modules]

    created = client.post(
        "/roles/",
        json={"name": f"Auditoría {uuid4().hex[:8]}", "description": "rol"},
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    role_id = created.json()["id"]

    response = client.post(
        f"/role-modules/{role_id}",
        headers=admin_headers,
        json={"module_ids": module_ids},
    )
    assert response.status_code == 200, response.text

    rows = _audit_rows(client, admin_headers, "role.modules_assigned")
    assert rows
    assert rows[0]["user_id"] == admin_user.id
    assert rows[0]["new_value"]["module_ids"] == module_ids

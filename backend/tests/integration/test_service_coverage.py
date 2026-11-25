from uuid import uuid4

import pytest
from sqlmodel import select

from src.modules.roles.models import Module
from src.modules.users.models import PasswordReset
from tests.conftest import TEST_USER_PASSWORD

pytestmark = pytest.mark.integration

NEW_PASSWORD = "Panaderia2026!"
FINAL_PASSWORD = "Panaderia2027!"


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:10]}"


def test_auth_service_full_flow(client, admin_user, db_session):
    first_login = client.post(
        "/session/login",
        json={"email": admin_user.email, "password": TEST_USER_PASSWORD},
    )
    assert first_login.status_code == 200
    first_token = first_login.json()["session_token"]

    change = client.post(
        "/session/change-password",
        json={"current_password": TEST_USER_PASSWORD, "new_password": NEW_PASSWORD},
        headers={"session-token": first_token},
    )
    assert change.status_code == 200

    second_login = client.post(
        "/session/login",
        json={"email": admin_user.email, "password": NEW_PASSWORD},
    )
    assert second_login.status_code == 200
    second_token = second_login.json()["session_token"]

    logout = client.post(
        "/session/logout",
        headers={"session-token": second_token, "session_token": second_token},
    )
    assert logout.status_code == 200

    third_login = client.post(
        "/session/login",
        json={"email": admin_user.email, "password": NEW_PASSWORD},
    )
    assert third_login.status_code == 200
    third_token = third_login.json()["session_token"]

    logout_all = client.post(
        "/session/logout-all", headers={"session-token": third_token}
    )
    assert logout_all.status_code == 200

    forgot = client.post(
        "/session/forgot-password", json={"email": admin_user.email}
    )
    assert forgot.status_code == 200

    reset_entry = db_session.exec(
        select(PasswordReset).where(PasswordReset.user_id == admin_user.id)
    ).first()
    assert reset_entry is not None

    reset = client.post(
        "/session/reset-password",
        json={"token": reset_entry.token, "new_password": FINAL_PASSWORD},
    )
    assert reset.status_code == 200

    final_login = client.post(
        "/session/login",
        json={"email": admin_user.email, "password": FINAL_PASSWORD},
    )
    assert final_login.status_code == 200


def test_users_service_lifecycle(client, admin_headers, admin_role, limited_headers):
    created = client.post(
        "/users/",
        json={
            "first_name": "Cobertura",
            "last_name": "Servicio",
            "email": f"{_unique('coverage-user')}@saip.com",
            "role_id": admin_role.id,
        },
        headers=admin_headers,
    )
    assert created.status_code == 201
    user_id = created.json()["id"]

    listed = client.get("/users/", headers=admin_headers)
    assert listed.status_code == 200

    updated = client.put(
        f"/users/{user_id}",
        json={"first_name": "Actualizado"},
        headers=admin_headers,
    )
    assert updated.status_code == 200

    deleted = client.delete(f"/users/{user_id}", headers=admin_headers)
    assert deleted.status_code == 200

    own_delete = client.delete(
        "/users/me",
        headers={**limited_headers, "X-Confirm-Password": TEST_USER_PASSWORD},
    )
    assert own_delete.status_code == 200


def test_products_and_commercial_products_service_lifecycle(
    client, admin_headers, unit, product
):
    category = client.post(
        "/product-categories/",
        json={"name": _unique("cat-comercial"), "description": "categoría e2e"},
        headers=admin_headers,
    )
    assert category.status_code == 201
    category_id = category.json()["id"]

    commercial = client.post(
        "/commercial-products/",
        json={
            "name": _unique("producto-comercial"),
            "category_id": category_id,
            "unit_id": unit["id"],
            "sale_price": 10,
        },
        headers=admin_headers,
    )
    assert commercial.status_code == 201
    commercial_id = commercial.json()["id"]

    product_update = client.patch(
        f"/products/{product['id']}",
        json={"description": "actualizado por cobertura"},
        headers=admin_headers,
    )
    assert product_update.status_code == 200

    for _ in range(2):
        lock = client.patch(
            f"/products/{product['id']}/lock", json={}, headers=admin_headers
        )
        assert lock.status_code == 200

    commercial_update = client.patch(
        f"/commercial-products/{commercial_id}",
        json={"sale_price": 12},
        headers=admin_headers,
    )
    assert commercial_update.status_code == 200

    assert client.delete(
        f"/commercial-products/{commercial_id}", headers=admin_headers
    ).status_code == 200
    assert client.delete(
        f"/products/{product['id']}", headers=admin_headers
    ).status_code == 204

    category_update = client.put(
        f"/product-categories/{category_id}",
        json={"description": "categoría actualizada"},
        headers=admin_headers,
    )
    assert category_update.status_code == 200
    assert client.delete(
        f"/product-categories/{category_id}", headers=admin_headers
    ).status_code == 200


def test_providers_and_supplies_service_lifecycle(client, admin_headers, unit):
    provider = client.post(
        "/providers/",
        json={
            "company": _unique("proveedor"),
            "nit": uuid4().hex[:12],
            "email": f"{_unique('proveedor')}@saip.com",
        },
        headers=admin_headers,
    )
    assert provider.status_code == 201
    provider_id = provider.json()["id"]

    provider_update = client.patch(
        f"/providers/{provider_id}", json={"company": "Proveedor actualizado"}, headers=admin_headers
    )
    assert provider_update.status_code == 200

    contact = client.post(
        f"/providers/{provider_id}/contacts/",
        json={"name": "Contacto cobertura", "email": f"{_unique('contacto')}@saip.com"},
        headers=admin_headers,
    )
    assert contact.status_code == 201
    contact_id = contact.json()["id"]

    contact_update = client.patch(
        f"/providers/{provider_id}/contacts/{contact_id}",
        json={"phone": "3001234567"},
        headers=admin_headers,
    )
    assert contact_update.status_code == 200
    assert client.delete(
        f"/providers/{provider_id}/contacts/{contact_id}", headers=admin_headers
    ).status_code == 200
    assert client.delete(
        f"/providers/{provider_id}", headers=admin_headers
    ).status_code == 200

    category = client.post(
        "/supply-categories/",
        json={"name": _unique("cat-insumo"), "description": "categoría e2e"},
        headers=admin_headers,
    )
    assert category.status_code == 201
    category_id = category.json()["id"]

    supply = client.post(
        "/supplies/",
        json={
            "name": _unique("insumo"),
            "category_id": category_id,
            "unit_id": unit["id"],
            "available_quantity": 10,
        },
        headers=admin_headers,
    )
    assert supply.status_code == 201
    supply_id = supply.json()["id"]

    supply_update = client.put(
        f"/supplies/{supply_id}",
        json={"description": "insumo actualizado", "available_quantity": 12},
        headers=admin_headers,
    )
    assert supply_update.status_code == 200
    assert client.delete(
        f"/supplies/{supply_id}", headers=admin_headers
    ).status_code == 200

    category_update = client.put(
        f"/supply-categories/{category_id}",
        json={"description": "categoría actualizada"},
        headers=admin_headers,
    )
    assert category_update.status_code == 200
    assert client.delete(
        f"/supply-categories/{category_id}", headers=admin_headers
    ).status_code == 200


def test_recipes_and_production_service_lifecycle(
    client, admin_headers, unit, product, db_session
):
    category = client.post(
        "/supply-categories/",
        json={"name": _unique("cat-receta"), "description": "categoría e2e"},
        headers=admin_headers,
    )
    assert category.status_code == 201

    supply = client.post(
        "/supplies/",
        json={
            "name": _unique("insumo-receta"),
            "category_id": category.json()["id"],
            "unit_id": unit["id"],
            "available_quantity": 100,
        },
        headers=admin_headers,
    )
    assert supply.status_code == 201

    recipe = client.post(
        "/recipes/",
        json={
            "name": _unique("receta"),
            "product_id": product["id"],
            "yield_quantity": 10,
            "yield_unit_id": unit["id"],
            "ingredients": [
                {
                    "supply_id": supply.json()["id"],
                    "quantity": 2,
                    "unit_id": unit["id"],
                }
            ],
        },
        headers=admin_headers,
    )
    assert recipe.status_code == 201
    recipe_id = recipe.json()["id"]

    recipe_update = client.patch(
        f"/recipes/{recipe_id}",
        json={"description": "receta actualizada"},
        headers=admin_headers,
    )
    assert recipe_update.status_code == 200

    order = client.post(
        "/production/orders/",
        json={"recipe_id": recipe_id, "quantity_multiplier": 1},
        headers=admin_headers,
    )
    assert order.status_code == 201
    order_id = order.json()["id"]

    assert client.get("/production/orders/", headers=admin_headers).status_code == 200
    assert client.get(
        f"/production/orders/{order_id}", headers=admin_headers
    ).status_code == 200
    assert client.patch(
        f"/production/orders/{order_id}/start", json={}, headers=admin_headers
    ).status_code == 200
    assert client.post(
        f"/production/orders/{order_id}/complete", json={}, headers=admin_headers
    ).status_code == 200

    cancelled_order = client.post(
        "/production/orders/",
        json={"recipe_id": recipe_id, "quantity_multiplier": 1},
        headers=admin_headers,
    )
    assert cancelled_order.status_code == 201
    assert client.patch(
        f"/production/orders/{cancelled_order.json()['id']}/cancel",
        json={"reason": "Prueba de cobertura"},
        headers=admin_headers,
    ).status_code == 200

    assert client.get(
        "/production/orders/export", headers=admin_headers
    ).status_code == 200
    assert client.delete(
        f"/recipes/{recipe_id}", headers=admin_headers
    ).status_code == 200


def test_roles_service_lifecycle(client, admin_headers, admin_role, db_session):
    module = Module(name=_unique("module"), label="Módulo cobertura")
    db_session.add(module)
    db_session.commit()
    db_session.refresh(module)

    role = client.post(
        "/roles/",
        json={"name": _unique("rol-cobertura"), "description": "rol e2e"},
        headers=admin_headers,
    )
    assert role.status_code == 201
    role_id = role.json()["id"]

    role_update = client.patch(
        f"/roles/{role_id}",
        json={"description": "rol actualizado"},
        headers=admin_headers,
    )
    assert role_update.status_code == 200

    modules = client.get("/role-modules/modules", headers=admin_headers)
    assert modules.status_code == 200

    assigned = client.post(
        f"/role-modules/{role_id}",
        json={"module_ids": [module.id]},
        headers=admin_headers,
    )
    assert assigned.status_code in (200, 201)

    assert client.get(
        f"/role-modules/{role_id}", headers=admin_headers
    ).status_code == 200
    assert client.delete(f"/roles/{role_id}", headers=admin_headers).status_code == 204


def test_sales_service_list_and_export(client, admin_headers, sale):
    listed = client.get(
        "/sales/", headers=admin_headers, params={"status": "completada"}
    )
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1

    exported = client.get("/sales/export", headers=admin_headers)
    assert exported.status_code == 200

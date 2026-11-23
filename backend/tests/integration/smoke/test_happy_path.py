"""Happy path representativo por módulo (red de seguridad de la Fase 0).

No busca cubrir los 94 endpoints uno por uno: ejercita el flujo principal de
cada dominio para detectar regresiones gruesas en las fases siguientes.
"""

from datetime import date, timedelta
from uuid import uuid4

import pytest

from tests.conftest import TEST_USER_PASSWORD

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:10]}"


# --- Auth -----------------------------------------------------------------


def test_login_rejects_wrong_password(client, admin_user):
    response = client.post(
        "/session/login",
        json={"email": admin_user.email, "password": "clave-incorrecta"},
    )

    assert response.status_code == 401
    assert "detail" in response.json()


def test_login_accepts_valid_credentials_and_logout_works(client, admin_user):
    response = client.post(
        "/session/login",
        json={"email": admin_user.email, "password": TEST_USER_PASSWORD},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["user"]["email"] == admin_user.email
    assert body["session_token"]

    headers = {"session-token": body["session_token"]}
    assert client.get("/users/me", headers=headers).status_code == 200

    # ``POST /session/logout`` usa el alias ``session_token`` (guion bajo).
    logout = client.post(
        "/session/logout",
        headers={**headers, "session_token": body["session_token"]},
    )
    assert logout.status_code == 200, logout.text
    assert "message" in logout.json()

    # La sesión queda inactiva tras cerrar sesión.
    assert client.get("/users/me", headers=headers).status_code == 401


# --- Usuarios y roles -----------------------------------------------------


def test_users_me_and_listing(client, admin_headers, admin_user):
    me = client.get("/users/me", headers=admin_headers)
    assert me.status_code == 200, me.text
    assert me.json()["email"] == admin_user.email

    listing = client.get("/users/", headers=admin_headers)
    assert listing.status_code == 200, listing.text
    body = listing.json()
    assert isinstance(body, list)
    assert any(user["id"] == admin_user.id for user in body)


def test_public_user_creation_returns_created_user(client, limited_role):
    payload = {
        "first_name": "Nuevo",
        "last_name": "Usuario",
        "email": f"{uuid4().hex[:10]}@saip.com",
        "role_id": limited_role.id,
        "is_admin": False,
    }

    response = client.post("/users/", json=payload)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["id"] > 0
    assert body["email"] == payload["email"].lower()


def test_roles_listing_and_public_creation(client, admin_headers):
    listing = client.get("/roles/", headers=admin_headers)
    assert listing.status_code == 200, listing.text
    assert isinstance(listing.json(), list)

    created = client.post(
        "/roles/", json={"name": _unique("rol"), "description": "rol de prueba"}
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["id"] > 0
    assert body["description"] == "rol de prueba"


# --- Catálogos ------------------------------------------------------------


@pytest.fixture()
def unit(client, admin_headers):
    response = client.post(
        "/units/",
        json={
            "name": _unique("unidad"),
            "abbreviation": uuid4().hex[:10],
            "description": "unidad de prueba",
            "quantity": 1,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture()
def supply_category(client, admin_headers):
    response = client.post(
        "/supply-categories/",
        json={"name": _unique("categoria-insumo"), "description": "prueba"},
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture()
def supply(client, admin_headers, supply_category, unit):
    response = client.post(
        "/supplies/",
        json={
            "name": _unique("insumo"),
            "description": "insumo de prueba",
            "category_id": supply_category["id"],
            "unit_id": unit["id"],
            "available_quantity": 100,
            "min_stock": 10,
            "max_stock": 200,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture()
def product(client, admin_headers, unit):
    response = client.post(
        "/products/",
        json={
            "name": _unique("producto"),
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
def commercial_category(client, admin_headers):
    response = client.post(
        "/product-categories/",
        json={"name": _unique("categoria-producto"), "description": "prueba"},
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture()
def commercial_product(client, admin_headers, commercial_category, unit):
    response = client.post(
        "/commercial-products/",
        json={
            "name": _unique("producto-comercial"),
            "description": "producto comercial de prueba",
            "category_id": commercial_category["id"],
            "unit_id": unit["id"],
            "purchase_price": 1000,
            "sale_price": 2000,
            "available_quantity": 30,
            "min_stock": 5,
            "max_stock": 60,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture()
def provider(client, admin_headers):
    response = client.post(
        "/providers/",
        json={
            "company": _unique("Proveedor"),
            "nit": uuid4().hex[:12],
            "email": f"{uuid4().hex[:10]}@saip.com",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_units_full_crud(client, admin_headers):
    created = client.post(
        "/units/",
        json={
            "name": _unique("unidad-crud"),
            "abbreviation": uuid4().hex[:10],
            "description": "crud",
            "quantity": 2,
        },
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    unit_id = created.json()["id"]

    fetched = client.get(f"/units/{unit_id}")
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["id"] == unit_id

    updated = client.patch(
        f"/units/{unit_id}", json={"quantity": 7}, headers=admin_headers
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["quantity"] == 7

    deleted = client.delete(f"/units/{unit_id}", headers=admin_headers)
    assert deleted.status_code == 204

    assert client.get(f"/units/{unit_id}").status_code == 404


def test_products_can_be_created_listed_and_locked(client, admin_headers, unit):
    created = client.post(
        "/products/",
        json={
            "name": _unique("producto-crud"),
            "description": "producto",
            "unit_id": unit["id"],
            "available_quantity": 40,
            "min_stock": 5,
            "max_stock": 80,
        },
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    product_id = created.json()["id"]

    listing = client.get("/products/")
    assert listing.status_code == 200, listing.text
    assert isinstance(listing.json(), list)

    fetched = client.get(f"/products/{product_id}")
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["is_locked"] is False

    locked = client.patch(f"/products/{product_id}/lock", headers=admin_headers)
    assert locked.status_code == 200, locked.text
    assert locked.json()["is_locked"] is True


def test_supply_categories_and_supplies(client, admin_headers, supply_category, supply):
    categories = client.get("/supply-categories/", headers=admin_headers)
    assert categories.status_code == 200, categories.text
    assert any(item["id"] == supply_category["id"] for item in categories.json())

    supplies = client.get("/supplies/", headers=admin_headers)
    assert supplies.status_code == 200, supplies.text
    assert any(item["id"] == supply["id"] for item in supplies.json())

    fetched = client.get(f"/supplies/{supply['id']}", headers=admin_headers)
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["available_quantity"] == 100

    updated = client.put(
        f"/supplies/{supply['id']}",
        json={"available_quantity": 120},
        headers=admin_headers,
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["available_quantity"] == 120


def test_commercial_products_are_listed(
    client, admin_headers, commercial_category, commercial_product
):
    categories = client.get("/product-categories/", headers=admin_headers)
    assert categories.status_code == 200, categories.text
    assert any(item["id"] == commercial_category["id"] for item in categories.json())

    listing = client.get("/commercial-products/", headers=admin_headers)
    assert listing.status_code == 200, listing.text
    assert any(item["id"] == commercial_product["id"] for item in listing.json())

    fetched = client.get(
        f"/commercial-products/{commercial_product['id']}", headers=admin_headers
    )
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["sale_price"] == 2000


def test_providers_and_contacts(client, admin_headers, provider):
    listing = client.get("/providers/", headers=admin_headers)
    assert listing.status_code == 200, listing.text
    assert any(item["id"] == provider["id"] for item in listing.json())

    contact = client.post(
        f"/providers/{provider['id']}/contacts/",
        json={"name": "Contacto Prueba", "email": "contacto@saip.com"},
        headers=admin_headers,
    )
    assert contact.status_code == 201, contact.text
    assert contact.json()["provider_id"] == provider["id"]

    fetched = client.get(f"/providers/{provider['id']}", headers=admin_headers)
    assert fetched.status_code == 200, fetched.text
    assert len(fetched.json()["contacts"]) == 1


# --- Recetas, producción y ventas ----------------------------------------


@pytest.fixture()
def recipe(client, admin_headers, product, supply, unit):
    response = client.post(
        "/recipes/",
        json={
            "name": _unique("receta"),
            "description": "receta de prueba",
            "product_id": product["id"],
            "yield_quantity": 10,
            "yield_unit_id": unit["id"],
            "ingredients": [
                {
                    "supply_id": supply["id"],
                    "quantity": 2,
                    "unit_id": unit["id"],
                    "notes": "ingrediente de prueba",
                }
            ],
        },
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_recipes_can_be_created_listed_and_updated(client, admin_headers, recipe):
    listing = client.get("/recipes/", headers=admin_headers)
    assert listing.status_code == 200, listing.text
    assert any(item["id"] == recipe["id"] for item in listing.json())

    fetched = client.get(f"/recipes/{recipe['id']}", headers=admin_headers)
    assert fetched.status_code == 200, fetched.text
    assert len(fetched.json()["ingredients"]) == 1

    updated = client.patch(
        f"/recipes/{recipe['id']}",
        json={"yield_quantity": 12},
        headers=admin_headers,
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["yield_quantity"] == 12


def test_production_order_lifecycle(client, admin_headers, recipe, product, supply):
    created = client.post(
        "/production/orders/",
        json={"recipe_id": recipe["id"], "quantity_multiplier": 1},
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    order = created.json()
    assert order["status"] == "pending"
    order_id = order["id"]

    listing = client.get("/production/orders/", headers=admin_headers)
    assert listing.status_code == 200, listing.text
    assert any(item["id"] == order_id for item in listing.json())

    started = client.patch(
        f"/production/orders/{order_id}/start", headers=admin_headers
    )
    assert started.status_code == 200, started.text
    assert started.json()["status"] == "in_progress"

    completed = client.post(
        f"/production/orders/{order_id}/complete", headers=admin_headers
    )
    assert completed.status_code == 200, completed.text
    body = completed.json()
    assert body["status"] == "completed"
    assert body["product_quantity_added"] == 10
    assert len(body["snapshots"]) == 1

    # El producto sumó el rendimiento y el insumo consumió la cantidad usada.
    product_after = client.get(f"/products/{product['id']}")
    assert product_after.json()["available_quantity"] == 60

    supply_after = client.get(f"/supplies/{supply['id']}", headers=admin_headers)
    assert supply_after.json()["available_quantity"] == 98


def test_sale_creation_listing_and_annulment(client, admin_headers, product):
    created = client.post(
        "/sales/",
        json={
            "items": [
                {"item_type": "product", "item_id": product["id"], "quantity": 2}
            ],
            "notes": "venta de prueba",
        },
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    sale = created.json()["sale"]
    assert sale["status"] == "completada"
    assert len(sale["items"]) == 1
    sale_id = sale["id"]

    listing = client.get("/sales/", headers=admin_headers)
    assert listing.status_code == 200, listing.text
    page = listing.json()
    assert {"items", "total", "page", "limit"} <= set(page)
    assert page["total"] >= 1

    fetched = client.get(f"/sales/{sale_id}", headers=admin_headers)
    assert fetched.status_code == 200, fetched.text

    after_sale = client.get(f"/products/{product['id']}")
    assert after_sale.json()["available_quantity"] == 48

    annulled = client.patch(
        f"/sales/{sale_id}/annul",
        headers=admin_headers,
        json={"reason": "Prueba de anulación de la suite smoke"},
    )
    assert annulled.status_code == 200, annulled.text
    assert annulled.json()["status"] == "anulada"

    restored = client.get(f"/products/{product['id']}")
    assert restored.json()["available_quantity"] == 50


# --- Inventario, estadísticas y reportes ---------------------------------


def test_inventory_summary_and_report(client, admin_headers, supply, product):
    summary = client.get("/inventory/summary", headers=admin_headers)
    assert summary.status_code == 200, summary.text
    body = summary.json()
    assert {"items", "total", "page", "limit", "summary"} <= set(body)
    assert body["total"] >= 2

    report = client.get("/inventory/report", headers=admin_headers)
    assert report.status_code == 200, report.text
    assert report.headers["content-type"] == XLSX_MIME
    assert report.content


def test_stats_dashboard(client, admin_headers, supply, product):
    response = client.get("/stats/dashboard", headers=admin_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert {"kpis", "ventas", "produccion", "productos"} <= set(body)


REPORT_ENTITIES = [
    "users",
    "roles",
    "sessions",
    "products",
    "supplies",
    "supply-categories",
    "units",
    "recipes",
    "production",
    "providers",
    "product-categories",
    "commercial-products",
]


@pytest.mark.parametrize("entity", REPORT_ENTITIES)
def test_reports_generate_an_excel_file(
    client, admin_headers, supply, product, recipe, entity
):
    response = client.get(
        f"/reports/{entity}",
        headers=admin_headers,
        params={
            "fecha_inicio": (date.today() - timedelta(days=1)).isoformat(),
            "fecha_fin": (date.today() + timedelta(days=1)).isoformat(),
        },
    )

    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == XLSX_MIME
    assert response.content


def test_reports_support_json_format(client, admin_headers, product):
    response = client.get("/reports/products?format=json", headers=admin_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["entity"] == "products"
    assert {"total", "data", "filters_applied"} <= set(body)


BULK_TEMPLATES = [
    "/commercial-products/bulk/template",
    "/inventory/bulk/template",
    "/production/orders/bulk/template",
    "/products/bulk/template",
    "/providers/bulk/template",
    "/providers/contacts/bulk/template",
    "/supplies/bulk/template",
]


@pytest.mark.parametrize("url", BULK_TEMPLATES)
def test_bulk_templates_are_public_excel_files(client, url):
    response = client.get(url)

    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == XLSX_MIME
    assert response.content

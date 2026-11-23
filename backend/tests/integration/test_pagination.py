"""Tests del contrato de paginación (Fase 6, mínimo de la Fase 3.2).

Envelope ``{items, total, page, limit}`` en los tres listados pesados,
límites de ``limit`` y consistencia entre páginas (sin solapes ni huecos).
"""

from uuid import uuid4

import pytest


def _create_product(client, admin_headers, unit, suffix: str) -> dict:
    response = client.post(
        "/products/",
        json={
            "name": f"Producto paginado {suffix} {uuid4().hex[:6]}",
            "description": "producto para prueba de paginación",
            "unit_id": unit["id"],
            "available_quantity": 10,
            "min_stock": 1,
            "max_stock": 100,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_products_listing_returns_the_paginated_envelope(
    client, admin_headers
):
    response = client.get("/products/", headers=admin_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert set(body) == {"items", "total", "page", "limit"}
    assert body["page"] == 1
    assert body["limit"] == 20
    assert isinstance(body["items"], list)
    assert body["total"] == len(body["items"])


def test_pages_do_not_overlap_and_cover_every_row(
    client, admin_headers, unit
):
    created = [
        _create_product(client, admin_headers, unit, str(index))
        for index in range(3)
    ]
    created_ids = {product["id"] for product in created}

    first = client.get(
        "/products/?page=1&limit=2", headers=admin_headers
    ).json()
    second = client.get(
        "/products/?page=2&limit=2", headers=admin_headers
    ).json()

    assert first["total"] == 3
    assert second["total"] == 3
    assert len(first["items"]) == 2
    assert len(second["items"]) == 1

    first_ids = {item["id"] for item in first["items"]}
    second_ids = {item["id"] for item in second["items"]}

    # Sin solapes, sin huecos, y solo filas creadas por este test.
    assert first_ids.isdisjoint(second_ids)
    assert first_ids | second_ids == created_ids


@pytest.mark.parametrize(
    "query",
    ["?page=0", "?limit=0", "?limit=101", "?page=-1", "?limit=abc"],
)
def test_out_of_range_pagination_is_rejected(client, admin_headers, query):
    response = client.get(f"/products/{query}", headers=admin_headers)

    assert response.status_code == 422, response.text


def test_supplies_listing_is_paginated(client, admin_headers):
    response = client.get("/supplies/?limit=5", headers=admin_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert set(body) == {"items", "total", "page", "limit"}
    assert body["limit"] == 5


def test_search_filters_by_name(client, admin_headers, unit):
    marker = f"marcador-{uuid4().hex[:8]}"
    match = _create_product(client, admin_headers, unit, "match")
    client.post(
        "/products/",
        json={
            "name": f"Otro producto {marker}",
            "description": "sin relación",
            "unit_id": unit["id"],
            "available_quantity": 1,
            "min_stock": 0,
            "max_stock": 10,
        },
        headers=admin_headers,
    )

    # Se busca por el nombre único del primer producto.
    response = client.get(
        "/products/", params={"search": match["name"]}, headers=admin_headers
    )
    body = response.json()

    assert response.status_code == 200, response.text
    assert body["total"] == 1
    assert body["items"][0]["id"] == match["id"]


def test_search_escapes_like_wildcards(client, admin_headers, unit):
    _create_product(client, admin_headers, unit, "plain")
    # Un "%" solo no debe devolver todo: se busca literal.
    response = client.get(
        "/products/", params={"search": "%"}, headers=admin_headers
    )

    assert response.status_code == 200, response.text
    assert response.json()["total"] == 0


def test_commercial_products_listing_is_paginated(client, admin_headers):
    response = client.get(
        "/commercial-products/?limit=5", headers=admin_headers
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert set(body) == {"items", "total", "page", "limit"}
    assert body["limit"] == 5

"""Smoke de autorización sobre los 94 endpoints.

Contrato observado en el código actual (Fase 0, no se corrige aquí):

* Si falta el header ``session-token`` la respuesta es **422** (validación),
  no 401. El 401 aparece cuando el token existe pero es inválido.
* ``POST /session/logout`` usa el alias ``session_token`` (guion bajo).
* ``POST /role-modules/{role_id}`` y ``GET /audit/`` exigen ``require_admin``.
* ``/inventory/report`` y ``/inventory/summary`` exigen el módulo
  ``inventory``; ``PATCH /sales/{sale_id}/annul`` exige ``sales``.
"""

import re

import pytest

from tests.smoke.route_matrix import ROUTE_MATRIX, route_id

PROTECTED = [case for case in ROUTE_MATRIX if case.auth != "public"]
PUBLIC = [case for case in ROUTE_MATRIX if case.auth == "public"]
ADMIN_ONLY = [case for case in ROUTE_MATRIX if case.auth == "admin"]
MODULE_PROTECTED = [case for case in ROUTE_MATRIX if case.auth.startswith("module:")]
DETAIL_WITH_PARAM = [
    case
    for case in ROUTE_MATRIX
    if case.happy == "detail" and case.auth != "public" and "{" in case.path
]

INVALID_TOKEN = {"session-token": "esto-no-es-un-jwt"}


def _url(path: str) -> str:
    """Reemplaza los parámetros de ruta por un id inexistente."""
    return re.sub(r"\{[^}]+\}", "999999", path)


@pytest.mark.parametrize("case", PROTECTED, ids=route_id)
def test_protected_route_without_token_returns_422(client, case):
    response = client.request(case.method, _url(case.path))

    assert response.status_code == 422, (
        f"{case.method} {case.path} devolvió {response.status_code}; se esperaba "
        "422 por el header session-token ausente"
    )


@pytest.mark.parametrize("case", PROTECTED, ids=route_id)
def test_protected_route_with_invalid_token_returns_401(client, case):
    response = client.request(case.method, _url(case.path), headers=INVALID_TOKEN)

    assert response.status_code == 401, (
        f"{case.method} {case.path} devolvió {response.status_code}; se esperaba 401"
    )


@pytest.mark.parametrize("case", PUBLIC, ids=route_id)
def test_public_route_does_not_demand_a_token(client, case):
    response = client.request(case.method, _url(case.path))

    assert response.status_code not in (401, 403), (
        f"{case.method} {case.path} es público pero devolvió {response.status_code}"
    )


@pytest.mark.parametrize("case", ADMIN_ONLY, ids=route_id)
def test_admin_route_denies_a_non_admin_user(client, case, limited_headers):
    response = client.request(
        case.method, _url(case.path), headers=limited_headers
    )

    assert response.status_code == 403, (
        f"{case.method} {case.path} devolvió {response.status_code}; un usuario sin "
        "is_admin debía recibir 403"
    )


@pytest.mark.parametrize("case", ADMIN_ONLY, ids=route_id)
def test_admin_route_allows_an_admin_user(client, case, admin_headers):
    response = client.request(case.method, _url(case.path), headers=admin_headers)

    assert response.status_code not in (401, 403), (
        f"{case.method} {case.path} devolvió {response.status_code} con un admin"
    )


@pytest.mark.parametrize("case", MODULE_PROTECTED, ids=route_id)
def test_module_route_denies_a_user_without_the_module(client, case, limited_headers):
    response = client.request(
        case.method, _url(case.path), headers=limited_headers
    )

    assert response.status_code == 403, (
        f"{case.method} {case.path} devolvió {response.status_code}; se esperaba 403 "
        "por no tener el módulo RBAC"
    )


@pytest.mark.parametrize("case", MODULE_PROTECTED, ids=route_id)
def test_module_route_allows_an_admin_user(client, case, admin_headers):
    response = client.request(case.method, _url(case.path), headers=admin_headers)

    assert response.status_code not in (401, 403), (
        f"{case.method} {case.path} devolvió {response.status_code}; is_admin debe "
        "saltar la validación de módulo"
    )


@pytest.mark.parametrize("case", DETAIL_WITH_PARAM, ids=route_id)
def test_detail_route_with_valid_token_reaches_the_service(client, case, admin_headers):
    response = client.request(case.method, _url(case.path), headers=admin_headers)

    assert response.status_code == 404, (
        f"{case.method} {case.path} devolvió {response.status_code}; con un id "
        "inexistente y token válido se esperaba 404"
    )

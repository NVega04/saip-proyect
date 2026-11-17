"""La matriz de rutas debe reflejar exactamente la aplicación real.

Si este test falla, hay un endpoint nuevo o eliminado que no está clasificado en
``route_matrix.py`` (y probablemente tampoco en ``docs/INVENTARIO.md``).
"""

from fastapi.routing import APIRoute

from src.main import app
from tests.smoke.route_matrix import ROUTE_MATRIX

EXCLUDED_PATHS = {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}
IGNORED_METHODS = {"HEAD", "OPTIONS"}
ALLOWED_AUTH = {"public", "user", "admin"}
ALLOWED_HAPPY = {"probe", "list", "detail", "file", "readonly", "write"}


def _application_routes() -> set[tuple[str, str]]:
    routes: set[tuple[str, str]] = set()
    for route in app.routes:
        if not isinstance(route, APIRoute) or route.path in EXCLUDED_PATHS:
            continue
        for method in route.methods:
            if method in IGNORED_METHODS:
                continue
            routes.add((method, route.path))
    return routes


def _format(missing: list[tuple[str, str]]) -> str:
    return "\n".join(f"  {method:7} {path}" for method, path in missing)


def test_matrix_matches_the_application_routes():
    matrix = {(case.method, case.path) for case in ROUTE_MATRIX}
    application_routes = _application_routes()

    missing_in_matrix = sorted(application_routes - matrix)
    stale_in_matrix = sorted(matrix - application_routes)

    assert not missing_in_matrix, (
        "Endpoints de la aplicación sin clasificar en route_matrix.py:\n"
        + _format(missing_in_matrix)
    )
    assert not stale_in_matrix, (
        "Entradas de route_matrix.py que ya no existen en la aplicación:\n"
        + _format(stale_in_matrix)
    )


def test_matrix_has_no_duplicates_and_expected_size():
    pairs = [(case.method, case.path) for case in ROUTE_MATRIX]

    assert len(pairs) == len(set(pairs)), "Hay rutas duplicadas en la matriz"
    assert len(ROUTE_MATRIX) == 93, (
        f"La matriz tiene {len(ROUTE_MATRIX)} rutas; se esperaban 93"
    )


def test_matrix_uses_known_classification_values():
    for case in ROUTE_MATRIX:
        is_module = case.auth.startswith("module:") and len(case.auth) > len("module:")
        assert case.auth in ALLOWED_AUTH or is_module, (
            f"auth inválido en {case.method} {case.path}: {case.auth!r}"
        )
        assert case.happy in ALLOWED_HAPPY, (
            f"happy inválido en {case.method} {case.path}: {case.happy!r}"
        )

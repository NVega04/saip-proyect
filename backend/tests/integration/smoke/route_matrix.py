"""Matriz de cobertura de los 94 endpoints de SAIP.

Cada entrada declara cómo se autentica la ruta (corregido en Fase 6: solo health y session son públicos). ``test_route_coverage.py``
compara esta matriz contra ``app.routes``: si se agrega o elimina un endpoint
sin actualizarla, la suite falla. El campo ``happy`` describe el tipo de caso
feliz que cubre la suite y se usa como documentación viva del inventario.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteCase:
    method: str
    path: str
    auth: str  # public | user | admin | module:<nombre>
    happy: str  # probe | list | detail | file | readonly | write
    notes: str = ""


ROUTE_MATRIX: tuple[RouteCase, ...] = (
    RouteCase('GET', '/audit/', 'admin', 'list', 'Solo administradores.'),
    RouteCase('GET', '/commercial-products/', 'user', 'list', ''),
    RouteCase('POST', '/commercial-products/', 'user', 'write', ''),
    RouteCase('POST', '/commercial-products/bulk/import', 'user', 'write', ''),
    RouteCase('GET', '/commercial-products/bulk/template', 'user', 'file', ''),
    RouteCase('DELETE', '/commercial-products/{product_id}', 'user', 'write', ''),
    RouteCase('GET', '/commercial-products/{product_id}', 'user', 'detail', ''),
    RouteCase('PATCH', '/commercial-products/{product_id}', 'user', 'write', ''),
    RouteCase('GET', '/health', 'public', 'probe', 'Healthcheck; consulta SELECT 1 a la BD.'),
    RouteCase('GET', '/inventory/bulk/template', 'user', 'file', ''),
    RouteCase('GET', '/inventory/report', 'module:inventory', 'list', "Exige el módulo RBAC 'inventory'."),
    RouteCase('GET', '/inventory/summary', 'module:inventory', 'list', "Exige el módulo RBAC 'inventory'."),
    RouteCase('GET', '/product-categories/', 'user', 'list', ''),
    RouteCase('POST', '/product-categories/', 'user', 'write', ''),
    RouteCase('DELETE', '/product-categories/{category_id}', 'user', 'write', ''),
    RouteCase('GET', '/product-categories/{category_id}', 'user', 'detail', ''),
    RouteCase('PUT', '/product-categories/{category_id}', 'user', 'write', ''),
    RouteCase('GET', '/production/orders/', 'user', 'list', ''),
    RouteCase('POST', '/production/orders/', 'user', 'write', ''),
    RouteCase('POST', '/production/orders/bulk/import', 'user', 'write', ''),
    RouteCase('GET', '/production/orders/bulk/template', 'user', 'file', ''),
    RouteCase('GET', '/production/orders/export', 'user', 'file', ''),
    RouteCase('GET', '/production/orders/{order_id}', 'user', 'detail', ''),
    RouteCase('PATCH', '/production/orders/{order_id}/cancel', 'user', 'write', ''),
    RouteCase('POST', '/production/orders/{order_id}/complete', 'user', 'write', ''),
    RouteCase('PATCH', '/production/orders/{order_id}/start', 'user', 'write', ''),
    RouteCase('GET', '/products/', 'user', 'list', ''),
    RouteCase('POST', '/products/', 'user', 'write', ''),
    RouteCase('POST', '/products/bulk/import', 'user', 'write', ''),
    RouteCase('GET', '/products/bulk/template', 'user', 'file', ''),
    RouteCase('DELETE', '/products/{product_id}', 'user', 'write', ''),
    RouteCase('GET', '/products/{product_id}', 'user', 'detail', ''),
    RouteCase('PATCH', '/products/{product_id}', 'user', 'write', ''),
    RouteCase('PATCH', '/products/{product_id}/lock', 'user', 'write', ''),
    RouteCase('GET', '/providers/', 'user', 'list', ''),
    RouteCase('POST', '/providers/', 'user', 'write', ''),
    RouteCase('POST', '/providers/bulk/import', 'user', 'write', ''),
    RouteCase('GET', '/providers/bulk/template', 'user', 'file', ''),
    RouteCase('POST', '/providers/contacts/bulk/import', 'user', 'write', ''),
    RouteCase('GET', '/providers/contacts/bulk/template', 'user', 'file', ''),
    RouteCase('DELETE', '/providers/{provider_id}', 'user', 'write', ''),
    RouteCase('GET', '/providers/{provider_id}', 'user', 'detail', ''),
    RouteCase('PATCH', '/providers/{provider_id}', 'user', 'write', ''),
    RouteCase('POST', '/providers/{provider_id}/contacts/', 'user', 'write', ''),
    RouteCase('DELETE', '/providers/{provider_id}/contacts/{contact_id}', 'user', 'write', ''),
    RouteCase('PATCH', '/providers/{provider_id}/contacts/{contact_id}', 'user', 'write', ''),
    RouteCase('GET', '/recipes/', 'user', 'list', ''),
    RouteCase('POST', '/recipes/', 'user', 'write', ''),
    RouteCase('DELETE', '/recipes/{recipe_id}', 'user', 'write', ''),
    RouteCase('GET', '/recipes/{recipe_id}', 'user', 'detail', ''),
    RouteCase('PATCH', '/recipes/{recipe_id}', 'user', 'write', ''),
    RouteCase('GET', '/reports/{entity}', 'user', 'file', ''),
    RouteCase('GET', '/role-modules/modules', 'user', 'list', ''),
    RouteCase('GET', '/role-modules/{role_id}', 'user', 'detail', ''),
    RouteCase('POST', '/role-modules/{role_id}', 'admin', 'write', 'Exige require_admin.'),
    RouteCase('GET', '/roles/', 'user', 'list', ''),
    RouteCase('POST', '/roles/', 'user', 'write', ''),
    RouteCase('DELETE', '/roles/{role_id}', 'user', 'write', ''),
    RouteCase('PATCH', '/roles/{role_id}', 'user', 'write', ''),
    RouteCase('GET', '/sales/', 'user', 'list', ''),
    RouteCase('POST', '/sales/', 'user', 'write', ''),
    RouteCase('GET', '/sales/export', 'user', 'file', ''),
    RouteCase('GET', '/sales/{sale_id}', 'user', 'detail', ''),
    RouteCase('PATCH', '/sales/{sale_id}/annul', 'module:sales', 'write', "Exige el módulo RBAC 'sales' y motivo."),
    RouteCase('POST', '/session/change-password', 'user', 'write', ''),
    RouteCase('POST', '/session/forgot-password', 'public', 'write', ''),
    RouteCase('POST', '/session/login', 'public', 'write', ''),
    RouteCase('POST', '/session/logout', 'user', 'write', 'Usa el header session_token (guion bajo), distinto al resto.'),
    RouteCase('POST', '/session/logout-all', 'user', 'write', ''),
    RouteCase('POST', '/session/reset-password', 'public', 'write', ''),
    RouteCase('GET', '/stats/dashboard', 'user', 'readonly', ''),
    RouteCase('GET', '/supplies/', 'user', 'list', ''),
    RouteCase('POST', '/supplies/', 'user', 'write', ''),
    RouteCase('POST', '/supplies/bulk/import', 'user', 'write', ''),
    RouteCase('GET', '/supplies/bulk/template', 'user', 'file', ''),
    RouteCase('DELETE', '/supplies/{supply_id}', 'user', 'write', ''),
    RouteCase('GET', '/supplies/{supply_id}', 'user', 'detail', ''),
    RouteCase('PUT', '/supplies/{supply_id}', 'user', 'write', ''),
    RouteCase('GET', '/supply-categories/', 'user', 'list', ''),
    RouteCase('POST', '/supply-categories/', 'user', 'write', ''),
    RouteCase('DELETE', '/supply-categories/{category_id}', 'user', 'write', ''),
    RouteCase('GET', '/supply-categories/{category_id}', 'user', 'detail', ''),
    RouteCase('PUT', '/supply-categories/{category_id}', 'user', 'write', ''),
    RouteCase('GET', '/units/', 'user', 'list', ''),
    RouteCase('POST', '/units/', 'user', 'write', ''),
    RouteCase('DELETE', '/units/{unit_id}', 'user', 'write', ''),
    RouteCase('GET', '/units/{unit_id}', 'user', 'detail', ''),
    RouteCase('PATCH', '/units/{unit_id}', 'user', 'write', ''),
    RouteCase('GET', '/users/', 'user', 'list', ''),
    RouteCase('POST', '/users/', 'admin', 'write', 'Solo administradores: crea usuarios (incluido is_admin).'),
    RouteCase('DELETE', '/users/me', 'user', 'write', ''),
    RouteCase('GET', '/users/me', 'user', 'list', ''),
    RouteCase('DELETE', '/users/{user_id}', 'user', 'write', ''),
    RouteCase('PUT', '/users/{user_id}', 'user', 'write', ''),
)

def route_id(case: RouteCase) -> str:
    return f"{case.method} {case.path}"


def cases_with_auth(*prefixes: str) -> list[RouteCase]:
    return [c for c in ROUTE_MATRIX if c.auth.startswith(prefixes)]


def cases_excluding_auth(*prefixes: str) -> list[RouteCase]:
    return [c for c in ROUTE_MATRIX if not c.auth.startswith(prefixes)]

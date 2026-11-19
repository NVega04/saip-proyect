# Fase 4 — Reglas de negocio y trazabilidad

Rama: `fase-4-reglas-trazabilidad` (desde HEAD `5e2dd41`, igual a
`origin/master`). No se leyó ni modificó `.env`, no se tocaron migraciones ya
aplicadas y no se inició la Fase 5.

## Cambios por commit

1. `feat(audit): agregar trazabilidad de acciones críticas`
   - Modelo `AuditLog` (`audit_log`) con `user_id`, `action`, `resource_type`,
     `resource_id`, `old_value`, `new_value`, `ip_address` y `timestamp`.
   - `AuditService.log_action()` con sanitizado recursivo de claves sensibles
     (`password`, `token`, `secret`, `hash`, `jwt`, `credential`,
     `authorization`, `reset`) y `AuditReadService.list()` paginado, filtrable
     y también sanitizado en lectura.
   - `core/audit_context.py` captura `x-forwarded-for` o `request.client.host`.
   - `GET /audit/` con `require_admin`, filtros `action`/`user_id`, página y
     límite; registrado en `main.py` y `models_registry.py`.
   - Migración nueva `898807c7b86f` (hija de `756185c644ac`) con FK a
     `users.id` e índices en `user_id`, `action`, `resource_id` y `timestamp`.
   - Hooks en usuarios (`user.created` con `user_id=NULL` en el flujo público,
     `user.updated`, `user.deleted`, `user.self_deleted`), roles
     (`role.created`, `role.updated`, `role.deactivated`,
     `role.modules_assigned`), seguridad (`login.failed`, `login.locked`,
     `password.reset_requested`, `password.reset`, `password.changed`) y
     reportes (`report.downloaded` para JSON y Excel). Los factories inyectan
     `AuditContext.ip_address` y ningún hook guarda passwords ni tokens.
2. `feat(sales): reforzar anulación y actualizar contrato`
   - `modules/sales/state.py`: única transición permitida
     `COMPLETED → ANNULLED`, ventana máxima de 24 h y normalización de fechas
     naive de Bogotá a UTC.
   - `SaleAnnulRequest.reason` (3–500 caracteres) y anulación protegida con
     `SELECT ... FOR UPDATE` sobre la venta.
   - `PATCH /sales/{sale_id}/annul` ahora exige `require_module("sales")` y
     registra `sale.annulled` + un `inventory.movement_created` por ítem.
   - Errores de dominio se preservan con `DomainError` (400/404) en lugar de
     convertirse en 500 genérico.
   - Matriz de rutas actualizada a 94 endpoints; baseline OpenAPI actualizado
     con aprobación explícita: 60 paths, 123 schemas, SHA-256
     `d5b5f24dcf9683f3a1b5d74bac9a4659cba801f519233407fbf06ced6350607a`.
3. `docs(fase4): documentar trazabilidad y reglas de negocio`
   - Este documento, `docs/ARQUITECTURA.md` y `docs/INVENTARIO.md`
     actualizados a 94 endpoints, 22 tablas y 107 schemas propios.

## Pruebas agregadas

- `backend/tests/unit/test_sales_state.py`: transiciones, zona horaria y
  frontera de 24 h.
- `backend/tests/integration/test_audit_trail.py`: RBAC de `/audit/`,
  sanitizado en lectura, actor anónimo y asignación de módulos.
- `backend/tests/integration/test_sale_annulment.py`: motivo obligatorio,
  módulo RBAC, doble anulación, ventana vencida, stock intacto y auditoría de
  movimientos.
- Smoke actualizado: anulación con body `reason`, matriz de 94 rutas y
  expectativas de auth para `audit` y `sales`.

## Verificación

| Comprobación | Resultado |
|---|---|
| `docker compose exec -T backend uv run pytest -q` | **273 passed** (19 nuevos respecto a Fase 2) |
| `docker compose exec -T backend uv run alembic upgrade head` | `756185c644ac -> 898807c7b86f` aplicada en la base de desarrollo |
| `docker compose exec -T backend uv run alembic check` | `No new upgrade operations detected.` |
| `app.openapi()` | 60 paths, 123 schemas |
| `docker compose exec -T backend uv run python -c "from src.main import app; ..."` | aplicación importa correctamente |
| `.env` | no leído ni modificado |

## Decisiones y límites

- La anulación es la única transición de estado implementada porque `SaleStatus`
  solo define `COMPLETED` y `ANNULLED`.
- La ventana de 24 h se calcula en UTC; las fechas naive se interpretan como
  `America/Bogota`, coherente con `core/time.py`.
- El bloqueo pesimista evita la doble anulación concurrente; no se bloquean las
  filas de stock, que siguen con el manejo previo del servicio.
- Quedan fuera de alcance, como se acordó, los hooks de auditoría para
  importaciones bulk y producción.
- No se agregó frontend, CI ni cobertura: eso pertenece a la Fase 5.

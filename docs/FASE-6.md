# Fase 6 — Frontend, logging y documentación

Rama: `fase-6-frontend-logging-docs`. Plan guiado por `_docs/rules/ajustes.md`
(secciones 6.1–6.4). Todo se hizo con commits atómicos; **sin push** al cerrar.

## Resumen por bloques

| Bloque | Commit | Contenido |
|--------|--------|-----------|
| A — Logging | `8da7499` | `src/core/logging.py` (JSON estructurado, `LOG_LEVEL`/`LOG_FORMAT`, redacción de secretos) y `RequestIdMiddleware` (`X-Request-ID`). |
| B.1 — Paginación | `cecf749` | `page`/`limit` + envelope `{items, total, page, limit}` en products, supplies y commercial-products (1..100, defecto 20). |
| B.2 — Búsqueda | `3d1da99` | `search` con `LIKE` y comodines escapados en esos mismos listados. |
| C.1 — Frontend base | `aaa164c` | TanStack Query + `QueryClientProvider`, `apiFetch`/`toApiError`, hooks `useListQuery`/`usePagedQuery`, `AlertContext`, página Products. |
| C.2 — Frontend catálogos | `a8680ba` | Supplies y CommercialProducts migrados; dropdowns con `limit=100`. |
| C.3 — Frontend resto | `fdecf79` | Resto de listados, alertas y mensaje 429. |
| Seguridad (hallazgo) | `89a3af9` | Cierre de autorización y auditoría. |
| D — API docs | `cbe03ba` | `src/core/openapi.py`, 401 global, docstrings de reglas de negocio, snapshot. |
| E — Proyecto | *(commit de cierre `docs(proyecto)`)* | README, `ARQUITECTURA`, `SEGURIDAD`, `CONTRIBUIR`, `PENDIENTES`. |

## Hallazgo de seguridad corregido (`89a3af9`)

Durante la revisión se detectó que `POST /users/` y `POST /roles/` no tenían
ninguna dependencia de autorización: era posible crear un usuario con
`is_admin=true` y `role_id=1` **sin token** (reproducido y limpiado en dev).
También los listados/detalle de products y units y 7 plantillas bulk eran
públicos, a diferencia de módulos hermanos.

- `POST /users/` → `require_admin`; `POST /roles/` → `get_current_user`. Ambos
  auditan con el `user_id` del actor (antes `null`).
- Las rutas expuestas pasaron a exigir el header `session-token`.
- Solo quedan públicos `/health`, `/session/login`, `forgot-password` y
  `reset-password`, cubierto por `test_only_health_and_session_are_public`.
- Se aplicó en dev la migración pendiente `898807c7b86f` (tabla `audit_log`);
  sin ella las operaciones auditadas devolvían 500.
- Corrección del typo `descripcion` → `description` en respuestas 403/404/409/
  410 de `PATCH`/`DELETE /roles/{role_id}`.

## Documentación de la API (`cbe03ba`)

- No se añade `/api/v1`: el desarrollador decidió expresamente **no versionar**
  las rutas (cambio de contrato).
- `src/core/openapi.py` centraliza respuestas reutilizables con el formato real
  `{ "detail": ... }` para 400/401/403/404/409/410/423/429.
- `main.py` aplica el 401 global con `include_router(responses=AUTH_ERRORS)`;
  las respuestas declaradas por ruta prevalecen.
- 26 operaciones principales documentan reglas de negocio en el docstring
  (stock y anulación en 24 h de ventas, transiciones de producción, bloqueo de
  productos, términos/bloqueo/rate limit de sesión, auditoría, reportes, ...).
- Estado final: **93 operaciones**, 26 con `description`, 88 con 401. Códigos
  documentados: `400×6, 401×88, 403×6, 404×14, 409×9, 410×2, 423×1, 429×2`.

## Verificación final

```bash
docker exec saip_backend uv run pytest -q       # 319 passed
cd frontend && pnpm lint && pnpm build          # 0 errores / build OK
docker compose build                            # imágenes dev OK
```

Comprobaciones en vivo (con el entorno de desarrollo levantado):

- `POST /users/` sin token → 422; con token inválido → 401.
- `GET /products/` sin token → 422; con token → 200.
- `GET /audit/` con token → 200 (tabla `audit_log` ya migrada).
- Las 9 páginas migradas renderizan 10 filas + paginación con el usuario
  `admin@saip.com` / `admin123`.

El snapshot aprobado quedó en SHA-256
`658d496eae09f0738c19d2c2c3311ddd39ac145e9d81805bfb6baa5450474114`, con su
motivación en `backend/tests/snapshots/README.md`.

## Fuera de alcance

Los puntos no ejecutados de las fases 3 y 5 y la deuda técnica detectada están
en [`PENDIENTES.md`](./PENDIENTES.md).

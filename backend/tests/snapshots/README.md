# Snapshot OpenAPI — procedencia y política

`openapi_baseline.json` es el contrato OpenAPI aprobado de SAIP. Es la
referencia contra la que `tests/test_openapi_snapshot.py` verifica que la API
no cambie de forma accidental.

## Procedencia

| Dato | Valor |
|---|---|
| Commit de origen | `0f86777` (`master`, previo a `fase-1-arquitectura`) |
| Actualizado en | `fase-6-frontend-logging-docs` (cambio aprobado) |
| Generado con | `app.openapi()` de la aplicación actual |
| Paths | 60 |
| Schemas | 126 |
| SHA-256 | `658d496eae09f0738c19d2c2c3311ddd39ac145e9d81805bfb6baa5450474114` |

## Cambio aprobado en Fase 6

- `GET /products/`, `GET /supplies/` y `GET /commercial-products/`
  pasan de lista plana al envelope paginado `{items, total, page, limit}`
  con los query params `page` (>= 1) y `limit` (1..100, defecto 20)
  (mínimo de la Fase 3.2).
- Los mismos endpoints añaden `search` (nombre o descripción, `LIKE` con
  comodines escapados) para conservar el buscador de las páginas, que
  antes filtraba en el cliente sobre todos los registros.
- Nuevos schemas genéricos `Page_ProductResponse_`, `Page_SupplyResponse_`
  y `Page_CommercialProductResponse_` (123 → 126 schemas).

## Cambio aprobado en Fase 6 — cierre de autorización

Hallazgo verificado en código y en el entorno de desarrollo: `POST /users/`,
`POST /roles/`, los listados de products/units y las 7 plantillas bulk no
exigían sesión. En vivo se pudo crear un usuario con `is_admin=true` y
`role_id=1` sin token (registro eliminado después de la comprobación).

- `POST /users/` exige ahora `require_admin` (403 para usuarios sin
  `is_admin`); `POST /roles/` exige sesión. Ambos registros de auditoría
  guardan el `user_id` del actor en lugar de `null`.
- Las rutas antes públicas pasan a exigir el header `session-token`
  (parámetro que aparece ahora en el OpenAPI): listados y detalle de
  products/units, y las plantillas bulk de commercial-products, inventory,
  production, products, providers (2) y supplies.
- Solo quedan públicos `GET /health` y los endpoints de login y
  recuperación de contraseña de `/session`.
- Corrección del typo `descripcion` → `description` en las respuestas 403/404/
  409/410 de `PATCH` y `DELETE /roles/{role_id}`: el campo no estándar hacía
  que Swagger mostrara los genéricos "Conflict"/"Gone"/"Not Found".

## Cambio aprobado en Fase 6 — documentación de API

- Nuevo módulo `src/core/openapi.py` con respuestas reutilizables y ejemplos
  con el formato real de la API (`{"detail": "..."}`) para 400, 401, 403,
  404, 409, 410, 423 y 429.
- `main.py` aplica el 401 a todos los routers autenticados mediante
  `include_router(responses=...)`; las rutas con errores propios los declaran
  en el decorador (y prevalecen sobre los globales).
- 26 operaciones principales incluyen ahora `description` mediante docstrings
  con reglas de negocio: ventas (stock y anulación en 24 h), producción
  (transiciones y consumo de insumos), productos (bloqueo, paginación y
  importación), sesión (términos, bloqueo y rate limit), auditoría, reportes
  y creación de usuarios/roles.
- No se añade el prefijo `/api/v1`: el desarrollador decidió expresamente no
  versionar las rutas (sería un cambio de contrato).

## Cambio aprobado en Fase 4

- Se agregó `GET /audit/` con los schemas `AuditLogResponse` y `AuditLogPage`.
- Se agregó `SaleAnnulRequest.reason` al contrato de anulación de ventas.
- El owner del endpoint de anulación pasó a ser el módulo RBAC `sales`.

## Política

1. **Nunca** se regenera el snapshot para que un test pase.
2. Un cambio de contrato (ruta, método, schema, código de respuesta) debe ser
   intencional y aprobado por el equipo. En ese caso:
   - se actualiza `openapi_baseline.json`;
   - se actualiza la tabla de arriba (conteos y SHA-256);
   - se explica el motivo en el mensaje del commit.
3. Las diferencias de `servers` se ignoran por ser volátiles.
4. Los cambios de comportamiento que no alteran el contrato (lógica interna,
   contenido de un Excel, envío de correos) **no** los detecta este test; para
   eso están los tests de humo y los tests de integración.

## Cómo verificar

```bash
docker compose run --rm backend uv run pytest tests/test_openapi_snapshot.py -q
```

Resultado esperado: `2 passed` (comparación + forma del baseline).

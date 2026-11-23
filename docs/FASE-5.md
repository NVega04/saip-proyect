# Fase 5 — Testing completo

Rama: `fase-5-testing-completo` (desde `7745c73`, HEAD de Fase 4). No se leyó ni modificó `.env`, no se tocó `.gitignore`, no se crearon migraciones y el contrato OpenAPI quedó intacto.

## Estructura de pruebas

Los tests existentes se movieron con `git mv` a la estructura acordada; solo se ajustaron imports y rutas relativas, sin cambiar aserciones:

```text
backend/tests/
├── conftest.py
├── unit/
│   ├── test_cors.py
│   ├── test_email.py
│   ├── test_jwt_security.py
│   ├── test_login_security.py
│   ├── test_openapi_snapshot.py
│   ├── test_password_policy.py
│   ├── test_phase_regressions.py
│   ├── test_security_config.py
│   ├── test_sales_state.py
│   └── test_validation.py
├── integration/
│   ├── conftest.py
│   ├── smoke/
│   ├── test_audit_trail.py
│   ├── test_db_isolation.py
│   ├── test_sale_annulment.py
│   ├── test_service_coverage.py
│   └── test_validation_endpoints.py
└── e2e/
    └── test_sale_flow.py
```

Markers registrados en `backend/pyproject.toml`: `unit`, `integration`, `e2e`, `security`, `validation` y `regression`.

## Pruebas agregadas

1. **Seguridad**
   - Login exitoso con token JWT válido.
   - Login fallido por correo inexistente.
   - Login fallido por contraseña incorrecta.
   - Rate limit de `/session/login`: quinta petición permitida, sexta devuelta como `429`.

2. **Validaciones**
   - Frontera de longitud de contraseña (11 caracteres rechazada, 12 aceptada).
   - Motivo de anulación con mínimo 3 y máximo 500 caracteres.
   - Query params inválidos en `sales`, `inventory`, `audit`, `stats` y `reports` (`422`).
   - Paginación válida reflejada en la respuesta (`page`, `limit`, `items`).

3. **Regresión fases 2 y 4**
   - Un test por hallazgo corregido: JWT obligatorio, sin secreto por defecto, CORS configurable, política de contraseñas, contraseñas temporales, pistas compartidas con el frontend, enlaces de correo, sanitizado de auditoría y reglas de anulación.
   - Fase 3: **N/A**. No existe branch, documentación ni commit de la Fase 3 en el repositorio; solo el plan en `_docs/rules/ajustes.md:246-289`. No se inventaron pruebas para cambios que nunca se aplicaron.

4. **Cobertura de servicios**
   - Ciclos de usuario, autenticación, productos, productos comerciales, proveedores, contactos, insumos, categorías, recetas, órdenes de producción, roles, módulos y ventas.

5. **E2E**
   - Flujo completo con `TestClient`: login → crear unidad y producto → crear venta → anular venta → reporte JSON → auditoría de `sale.annulled`.

## Calidad y CI

- Se agregaron `ruff` y `mypy` como dependencias de desarrollo.
- Ruff: `select = ["E4", "E7", "E9", "F"]`, con `E711`/`E712` ignorados por el uso intencional de comparaciones SQLAlchemy.
- Mypy: alcance limitado a módulos de seguridad y reglas críticas (`core/security.py`, `core/password.py`, `core/audit_context.py`, `core/exceptions.py`, `core/time.py`, `modules/audit/service.py`, `modules/sales/state.py`).
- `.github/workflows/backend-ci.yml` ejecuta en cada push/PR:
  - `uv sync --frozen`
  - `uv run ruff check .`
  - `uv run mypy`
  - `uv run alembic check`
  - `uv run pytest --cov=src --cov-report=term-missing:skip-covered`
- El workflow usa `db_saip_ci` como base de aplicación y `db_saip_test` como base de pruebas, sin coincidencias.

## Cambios de soporte

- `backend/pyproject.toml`: dependencias de desarrollo, markers y configuración de cobertura/ruff/mypy.
- `backend/uv.lock`: actualizado por `uv add --dev ruff mypy`.
- Correcciones menores para dejar los gates en verde: imports sin usar y uso de `col()` en `AuditService.list()`.
- No se cambió ninguna aserción de los tests preexistentes.

## Verificación

| Comprobación | Resultado |
|---|---|
| `docker compose exec -T backend uv run pytest -q -p no:warnings -p no:cacheprovider --cov=src --cov-report=term-missing:skip-covered` | **303 passed**, cobertura total **84.92 %** |
| Cobertura de servicios (`*/modules/*/service.py`) | **76 %** |
| Cobertura de seguridad (`core/security.py`, `core/password.py`, `core/config.py`, `core/email.py`, `core/audit_context.py`) | **95 %** |
| `docker compose exec -T backend uv run ruff check .` | `All checks passed!` |
| `docker compose exec -T backend uv run mypy` | `Success: no issues found in 7 source files` |
| `docker compose exec -T backend uv run alembic check` | `No new upgrade operations detected.` |
| `docker compose exec -T frontend pnpm exec tsc --noEmit` | Sin errores |
| `docker compose exec -T frontend pnpm lint` | 16 errores preexistentes, fuera del alcance de esta fase |
| `.env` / `.gitignore` / OpenAPI / migraciones | Intactos |

## Límites

- No se agregó Vitest ni Selenium; el alcance E2E acordado es backend con `TestClient`.
- La cobertura de bulk import sigue baja; no era prioridad de esta fase.
- Los 16 errores de ESLint del frontend quedan documentados para una fase posterior de frontend.

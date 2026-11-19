# Fase 0 — Preparación y red de seguridad

## Objetivo

Antes de tocar comportamiento, la Fase 0 construye una red de seguridad que
detecte regresiones en las fases siguientes. No se modificó código de la
aplicación, ni esquema, ni frontend: solo se agregó tooling de pruebas,
documentación y un inventario de la API.

## Rama y commits

- Rama: `fase-0-preparacion`, creada desde `fase-1-arquitectura`.
- Commits (en orden):

| Commit | Contenido |
|---|---|
| `812391d` | `chore(test)`: pytest, pytest-cov y httpx; configuración en `pyproject.toml` |
| `e8424c7` | `test(conftest)`: base de datos de test aislada y fixtures de autenticación |
| `5353c70` | `test(api)`: matriz de 93 rutas y smoke de autorización |
| `3b4edde` | `test(api)`: happy path de auth, users y roles |
| `b69ce51` | `test(api)`: happy path de catálogos (units, products, supplies, commercial, providers) |
| `d2f044e` | `test(api)`: happy path de recetas, producción, ventas, inventario, stats y reportes |
| `7dcc1cd` | `test(openapi)`: el snapshot pasa de script suelto a test de pytest |
| `afe8a63` | `docs(inventario)`: inventario de endpoints, modelos, schemas y deriva de Alembic |
| `1033bba` | `docs(fase-0)`: resumen de la fase, evidencia y deuda pendiente |
| `2b04270` | `chore(test)`: ignorar artefactos de pytest y cobertura |

## Qué se agregó

### 1. Tooling

`backend/pyproject.toml`:

- `[dependency-groups].dev`: `pytest>=8`, `pytest-cov>=5`, `httpx>=0.27`
  (se suman a `selenium` y `webdriver-manager`, que ya estaban).
- `[tool.pytest.ini_options]`: `pythonpath = ["."]`, `testpaths = ["tests"]`,
  `addopts = "-ra"` y el marker `smoke`.

### 2. Base de datos de test aislada

`backend/tests/conftest.py`:

- Construye el engine a partir de `DB_USER`, `DB_PASSWORD`, `DB_HOST`,
  `DB_PORT` y `TEST_DB_NAME` (por defecto `db_saip_test`). **No** modifica ni
  lee directamente `.env`; usa la configuración ya cargada por la app.
- Aborta si el nombre no termina en `_test` o si coincide con `DB_NAME`.
- Crea la base si no existe y recrea el esquema desde `SQLModel.metadata`
  (con `SET FOREIGN_KEY_CHECKS=0` por el ciclo `users` ↔ `roles`).
- Cada test corre en una transacción externa revertida al final; los
  `commit()` de los servicios se transforman en savepoints.
- Desactiva rate limits y envíos de correo.
- Fixtures: `admin_user`, `admin_headers`, `limited_role`, `limited_user`,
  `limited_headers`, `client`, `db_session`, `engine`.
- Contraseña de pruebas: `TEST_USER_PASSWORD = "Prueba123!"`.

### 3. Matriz de cobertura y autorización

`backend/tests/smoke/route_matrix.py` declara los **93 endpoints** con su
clasificación (`public`, `user`, `admin`, `module:inventory`) y el tipo de
caso feliz que cubre la suite.

`backend/tests/smoke/test_route_coverage.py` falla si `app.routes` y la
matriz dejan de coincidir (ruta nueva, eliminada o duplicada).

`backend/tests/smoke/test_unauthorized.py` fija el contrato observado:

- sin header `session-token` → **422** (no 401);
- token inválido → **401**;
- `require_admin` con usuario normal → **403**;
- módulo `inventory` sin asignación → **403**;
- rutas públicas no responden 401/403;
- detalle con id inexistente y token válido → **404**.

### 4. Happy path representativo

`backend/tests/smoke/test_happy_path.py` ejercita el flujo principal de cada
dominio, sin pretender cubrir los 93 endpoints uno por uno: login/logout,
usuarios, roles, CRUD de unidades, productos, insumos, categorías, productos
comerciales, proveedores y contactos, recetas, ciclo completo de producción,
venta y anulación, inventario, estadísticas, reportes (12 entidades) y
plantillas Excel.

### 5. Snapshot OpenAPI

`backend/tests/test_openapi_snapshot.py` sustituye al script
`tests/check_openapi_snapshot.py` (eliminado). Compara la app contra
`tests/snapshots/openapi_baseline.json` (commit `0f86777`, 59 paths, 120
schemas, SHA-256 `3f2bc1be…5902`). La procedencia y la política de
actualización están en `backend/tests/snapshots/README.md`.

### 6. Inventario

`docs/INVENTARIO.md` documenta, a partir del código real:

- los 93 endpoints con auth, código y schema de respuesta;
- las 21 tablas con PK, soft delete y FKs;
- los 104 schemas propios y los más reutilizados;
- dependencias compartidas, headers y códigos de error;
- 17 endpoints públicos y los riesgos asociados;
- el contrato OpenAPI y su snapshot;
- la deriva de Alembic (6 FKs) y la regla de mantenimiento.

## Resultado de la verificación

| Comprobación | Comando | Resultado |
|---|---|---|
| Suite completa | `uv run pytest -q` | **227 passed** en ~35 s |
| Cobertura | `uv run pytest --cov=src` | **73 %** de `src` |
| Healthcheck | `curl localhost:8000/health` | `{"status":"ok","db":"ok"}` |
| Compose de producción | `docker compose -f docker-compose.prod.yml config -q` | sin errores |
| Sin cambios de aplicación | `git diff --stat fase-1-arquitectura...HEAD -- backend/src backend/alembic frontend` | vacío |

Composición de la suite:

| Archivo | Tests |
|---|---:|
| `tests/test_db_isolation.py` | 3 |
| `tests/smoke/test_route_coverage.py` | 3 |
| `tests/smoke/test_unauthorized.py` | 184 |
| `tests/smoke/test_happy_path.py` | 35 |
| `tests/test_openapi_snapshot.py` | 2 |
| **Total** | **227** |

## Cómo ejecutar las pruebas

Con el stack levantado (rápido, reutiliza el `.venv` del contenedor):

```bash
docker compose exec backend uv run pytest -q
```

Con el stack apagado (crea un volumen anónimo para `/app/.venv`, por lo que
reinstala dependencias y tarda más):

```bash
docker compose run --rm backend uv run pytest -q
```

La base `db_saip_test` se crea sola en el contenedor de MySQL. Para usar otro
nombre, definir `TEST_DB_NAME` (debe terminar en `_test` y ser distinto de
`DB_NAME`).

## Hallazgos y decisiones

1. **`POST /users/` y `POST /roles/` son públicos.** Permiten crear cuentas y
   roles sin token. Se documenta en `docs/INVENTARIO.md`; corregirlo cambia
   comportamiento y corresponde a una fase de seguridad.
2. **Falta de header → 422.** No es un bug de la suite: es el contrato actual
   de FastAPI con `Header(...)`. Se fija en los tests en lugar de “arreglarlo”.
3. **`POST /session/logout` usa `session_token` (guion bajo).** Además ese
   header no está en `allow_headers` de CORS. Se documenta; no se corrige en
   esta fase.
4. **Deriva de Alembic (cerrada).** Una base creada solo con
   `alembic upgrade head` carecía de 6 FKs que sí están en los modelos
   (`commercial_products`, `product_categories` y `sales`: `updated_by` y
   `deleted_by`). Se corrigió en `fase-1-cierre-alembic` con la revisión
   `756185c644ac`, previa verificación de ausencia de filas huérfanas y con
   validación de upgrade/downgrade y `alembic check` limpio.
5. **`supply` no es un `item_type` válido en ventas.** El enum lo incluye,
   pero el servicio no lo resuelve y responde 404. Se documenta como
   comportamiento actual.
6. **Emails de prueba con `@saip.com`.** `EmailStr` rechaza dominios
   reservados como `.test`.
7. **Warnings de Pydantic v2.** Los `class Config` generan
   `PydanticDeprecatedSince20`; son preexistentes y no se tocaron.

## Deuda pendiente

- Proteger `POST /users/` y `POST /roles/` en la fase de seguridad.
- Unificar el header de logout (`session_token` → `session-token`) y agregarlo
  a CORS.
- Probar rate limit y bloqueo de cuenta (Fase 5).
- Agregar el workflow de CI que ejecute `uv run pytest -q` en cada PR.
- Evaluar pruebas de frontend (hoy no hay framework configurado).

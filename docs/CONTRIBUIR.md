# Guía para contribuir a SAIP

Convenciones de código y flujo de trabajo. Antes de empezar, lee
[`ARQUITECTURA.md`](./ARQUITECTURA.md) y el plan en `_docs/rules/ajustes.md`.

## Ramas y commits

- **Nunca** trabajes directamente en `main`. Crea una rama por bloque, p. ej.
  `fase-6-frontend-logging-docs`.
- Haz **commits pequeños y atómicos**: un cambio lógico por commit, con mensaje
  `tipo(ámbito): descripción` (ej. `feat(api): paginación en listados`).
- No subas (push) hasta que la verificación pase: backend tests, `pnpm lint` y
  `pnpm build`.
- No incluyas `.env` ni secretos en ningún commit; solo `.env.example`.

## Backend

### Estructura de un módulo

Cada dominio vive en `backend/src/modules/<modulo>/` con este reparto:

| Archivo | Responsabilidad |
|---------|-----------------|
| `models.py` | Modelos SQLModel (tablas, relaciones, soft-delete). |
| `schemas.py` | Modelos Pydantic de entrada/salida (nunca exponer `password_hash`). |
| `router.py` | Endpoints: validan dependencias y delegan en el servicio. Sin lógica de negocio. |
| `service.py` | Reglas de negocio, transacciones y escrituras en auditoría. |
| `dependencies.py` | `Depends` que construyen el servicio con la sesión. |

Reglas:

- Los servicios lanzan excepciones de `src/core/exceptions.py`
  (`NotFoundError`, `ConflictError`, `BusinessRuleError`, ...). El handler
  global de `main.py` las traduce a HTTP con `{ "detail": ... }`. **No** lances
  `HTTPException` desde un servicio.
- Usa `get_current_user` para exigir sesión y `require_module("...")` o
  `require_admin` para permisos. Toda ruta nueva debe quedar documentada como
  autenticada (el 401 global se aplica en `main.py`).
- Escribe la documentación OpenAPI en el **docstring** de la función y declara
  los errores propios en `responses={...}` con los helpers de
  `src/core/openapi.py`.
- Audita las operaciones críticas con `AuditService.log_action(...)` pasando
  siempre el `user_id` del actor. Los datos sensibles se sanitizan solos.
- Los soft-delete usan `deleted_at`/`deleted_by`; filtra por `deleted_at == None`
  en los listados.
- Si cambias modelos, crea una migración: `uv run alembic revision --autogenerate -m "..."`.

### Comandos

```bash
cd backend
uv sync                                   # instalar dependencias
uv run uvicorn src.main:app --reload       # servidor de desarrollo
uv run pytest -q                           # toda la suite
uv run pytest -q tests/test_password_policy.py
uv run alembic upgrade head                # aplicar migraciones
```

Con Docker (DB incluida):

```bash
docker compose up -d db
docker exec saip_backend uv run pytest -q
```

## Frontend

### Estructura

- `src/pages/` — páginas por módulo (`camelCase.tsx`).
- `src/components/` — componentes reutilizables (`PascalCase.tsx`).
- `src/context/` — Contextos de sesión (`AuthContext`), alertas
  (`AlertContext`) y confirmaciones (`ConfirmContext`).
- `src/hooks/` — `queries.ts` contiene `useListQuery` y `usePagedQuery`.
- `src/utils/` — `api.ts`, validaciones y permisos (`camelCase.ts`).
- CSS en `kebab-case.css`.

### Llamadas al API

- Usa siempre `apiFetch` (`src/utils/api.ts`): añade el header `session-token`
  desde `localStorage` y redirige al login en 401.
- Convierte los errores con `toApiError(response)` y muestra el mensaje con
  `useAlert()` de `AlertContext`. **No uses `alert()` nativo**.
- Los listados usan TanStack Query:

  ```tsx
  // Endpoint paginado (envelope {items, total, page, limit})
  const query = usePagedQuery<Product>("/products/", { page, limit: 20, search });
  const products = query.data?.items ?? [];

  // Endpoint que aún devuelve arreglo plano
  const roles = useListQuery<Role>("/roles/");
  ```

- Tras una mutación, invalida la clave:
  `queryClient.invalidateQueries({ queryKey: ["paged", "/products/"] })`.
- Los dropdowns que consumen listados paginados piden `limit=100` (tope del
  backend); esta limitación está anotada en `PENDIENTES.md`.

### Comandos

```bash
cd frontend
pnpm install
pnpm dev
pnpm lint                       # ESLint 9 flat config
pnpm lint src/pages/dashboard.tsx
pnpm build
```

> `pnpm build` usa Vite y no ejecuta `tsc`; existen errores de tipos
> preexistentes documentados en `PENDIENTES.md`. No los introduzcas en código
> nuevo.

## Contrato OpenAPI

- Swagger en `http://localhost:8000/docs`.
- El snapshot aprobado está en `backend/tests/snapshots/openapi_baseline.json`;
  cualquier cambio intencional del contrato debe regenerarse y explicarse en
  `backend/tests/snapshots/README.md`:

  ```bash
  docker exec saip_backend uv run pytest -q tests/test_openapi_snapshot.py
  ```

- No se usa prefijo `/api/v1`: decisión explícita de no versionar las rutas.

## Antes de abrir un PR

- [ ] `docker exec saip_backend uv run pytest -q` en verde.
- [ ] `pnpm lint` y `pnpm build` en verde.
- [ ] Snapshot OpenAPI actualizado si cambió el contrato.
- [ ] Sin secretos ni `.env` en el diff.
- [ ] Commit atómico con mensaje descriptivo.

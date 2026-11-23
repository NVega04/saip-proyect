# Trabajo pendiente

Deuda conocida y decisiones diferidas. **No está incluida** en la Fase 6
(`docs/FASE-6.md`); se documenta aquí para que no se pierda.

## Fases 3 y 5 del plan original

La **Fase 3 (seguridad P1)** ya fue ejecutada e integrada con Fase 6: rate
limit global y proxy de confianza, límites de reportes, validación de entrada
en servicios, cifrado de NIT/teléfonos con índice ciego, migración
`6ef9e1aec914`, scripts de respaldo y guía TLS/HSTS. Detalles en
[`SEGURIDAD.md`](./SEGURIDAD.md) y [`DEPLOY-SEGURIDAD.md`](./DEPLOY-SEGURIDAD.md).

Deuda derivada de las decisiones de integración:

- Se conservó la **paginación de Fase 6** (`page`/`limit`) y el **baseline
  OpenAPI aprobado**; por eso los límites de Fase 3 se validan en servicios en
  lugar de `Field(...)` en los schemas, y los 8 listados planos siguen sin tope
  (ver sección siguiente).
- No se añadió auditoría de acceso a registros individuales; solo se registran
  acciones críticas, con NIT/teléfonos sanitizados.

La **Fase 5 (infraestructura/CI)** tiene pipeline en
`.github/workflows/backend-ci.yml` (ruff, mypy, pytest y migraciones). Siguen
pendientes el despliegue automatizado y la monitorización centralizada de
logs/métricas más allá del logging JSON con `X-Request-ID`.

No se añadió el prefijo `/api/v1`: decisión explícita de **no versionar** el
contrato (cualquier cambio de rutas debe aprobarse antes).

## Paginación incompleta

Solo `GET /products/`, `GET /supplies/` y `GET /commercial-products/` usan
`page`/`limit` + envelope. Los siguientes listados siguen devolviendo un arreglo
plano y usan `useListQuery`:

- `/users/`, `/roles/`, `/units/`
- `/providers/`
- `/recipes/`
- `/production/orders/`
- `/supply-categories/`, `/product-categories/`

Migrarlos implica el mismo patrón (params `page`/`limit`, `search`, envelope y
`usePagedQuery`) y regenerar el snapshot OpenAPI. Las ventas y la auditoría sí
ya están paginadas.

## Dropdowns con tope de 100 registros

Los selectores que consumen los listados paginados piden `limit=100`, el valor
máximo permitido por el backend. Si un catálogo supera 100 elementos, el
dropdown no los mostrará todos. Solución pendiente: endpoint de búsqueda
remota (autocomplete) o permitir un `limit` mayor con control de rendimiento.

## Confirmaciones nativas

`frontend/src/pages/providers/Providers.tsx` todavía usa `window.confirm`.
Fue dejado fuera del alcance de la Fase 6 (solo se sustituyeron los `alert()`
por `AlertContext`). Hay un `ConfirmContext` disponible para migrarlo.

## Errores de tipos preexistentes en el frontend

`pnpm build` (Vite) pasa, pero `pnpm exec tsc --noEmit` reporta errores que
**no fueron introducidos** en la Fase 6 y que conviene corregir antes de
añadir `tsc` al pipeline:

- `src/components/bulkupload/BulkUploadModal.tsx` — import `React` sin usar y
  namespace `JSX` no resuelto.
- `src/components/chartcard/ChartCard.tsx` — namespace `JSX` no resuelto.
- `src/components/kpicard/KpiCard.tsx` — namespace `JSX` no resuelto.
- `src/pages/dashboard/Dashboard.tsx` — incompatibilidad de los `formatter`
  de Recharts con `ValueType | undefined` y del `label` del `Pie`.

## Tests del frontend

No hay framework de tests frontend (sin Vitest ni React Testing Library).
La verificación actual es `pnpm lint` + `pnpm build` y una prueba de humo
manual autenticada sobre las páginas migradas. La lista de 15 vistas con
doble prueba (positiva/negativa) en Selenium quedó como iniciativa separada
(`test_saip_15_vistas_doble_prueba.py`), no como parte de la suite del repo.

## Otros

- Los esquemas Pydantic con `class Config` (p. ej. `sales/schemas.py`) emiten
  `PydanticDeprecatedSince20`; migrar a `ConfigDict` antes de Pydantic 3.
- Los scripts de respaldo/restauración existen en `scripts/`, pero su
  programación (cron/job) y las pruebas periódicas de restauración siguen siendo
  responsabilidad del operador; ver [`SEGURIDAD.md`](./SEGURIDAD.md).
- La deuda de funcionalidad de negocio (p. ej. órdenes de compra) sigue en el
  README y en `docs/INVENTARIO.md`.

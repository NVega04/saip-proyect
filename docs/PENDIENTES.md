# Trabajo pendiente

Deuda conocida y decisiones diferidas. **No está incluida** en la Fase 6
(`docs/FASE-6.md`); se documenta aquí para que no se pierda.

## Fases 3 y 5 del plan original

El plan `_docs/rules/ajustes.md` contempla fases que **no se ejecutaron** en
esta rama:

- **Fase 3 — seguridad avanzada**: no hay rate limiting global (solo login
  5/min y recuperación 3/min), no hay cifrado de datos en reposo y no hay
  auditoría de acceso a registros individuales (solo acciones críticas).
- **Fase 5 — infraestructura/CI**: no hay pipeline de CI (no existe
  `.github/workflows`), no hay despliegue automatizado y no hay monitorización
  centralizada de logs/métricas más allá del logging JSON con `X-Request-ID`.
- No se añadió el prefijo `/api/v1`: decisión explícita de **no versionar** el
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
- No hay script automatizado de respaldo; el procedimiento manual está en
  [`SEGURIDAD.md`](./SEGURIDAD.md).
- La deuda de funcionalidad de negocio (p. ej. órdenes de compra) sigue en el
  README y en `docs/INVENTARIO.md`.

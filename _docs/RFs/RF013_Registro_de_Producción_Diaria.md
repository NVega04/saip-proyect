# RF-013 — Registro de producción diaria

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-013 |
| **Nombre** | Registro de producción diaria |
| **Módulo** | Producción |
| **Prioridad** | Alta |
| **Estado** | En progreso |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe permitir registrar la producción diaria mediante órdenes de producción asociadas a recetas. Las órdenes pasan por estados: `pending` → `in_progress` → `completed` / `cancelled`, con trazabilidad completa.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `recipe_id` | Entero | Sí | Debe existir y estar activa |
| `quantity_multiplier` | Decimal | Sí | Debe ser mayor a 0 |
| `scheduled_at` | Fecha | No | Fecha programada (opcional) |
| `notes` | Texto | No | Máximo 500 caracteres |

---

## Proceso

1. El usuario accede al módulo de producción y selecciona "Nueva orden".
2. Selecciona una receta, ingresa multiplicador y fecha programada.
3. Se crea la orden con estado `pending`.
4. El usuario puede iniciar la producción (cambia a `in_progress`).
5. Al completar (RF-012), se descuentan insumos y se cambia a `completed`.
6. También se puede cancelar la orden con estado `cancelled`.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Orden creada | 201 | Datos de la orden creada |
| Orden completada | 200 | Confirmación con descuentos |
| Orden cancelada | 200 | Confirmación de cancelación |
| Datos inválidos | 422 | Errores de validación |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| POST | `/production/orders/` | Sí | Crear orden de producción |
| GET | `/production/orders/` | Sí | Listar órdenes (filtro opcional `?status=`) |
| GET | `/production/orders/{id}` | Sí | Detalle de una orden |
| PATCH | `/production/orders/{id}/start` | Sí | Iniciar producción (`pending → in_progress`) |
| PATCH | `/production/orders/{id}/cancel` | Sí | Cancelar orden (`pending/in_progress → cancelled`) |
| POST | `/production/orders/{id}/complete` | Sí | Completar orden y descontar insumos (RF-012) |

> **Nota**: en lugar del `PATCH /production/orders/{id}` genérico previsto originalmente, se implementaron acciones explícitas (`/start`, `/cancel`, `/complete`). Esto impide transiciones de estado arbitrarias o inválidas y mantiene consistencia con el estilo de RF-012.

## Reglas de negocio

- **RN-073**: La receta debe existir y estar activa.
- **RN-074**: La orden inicia en estado `pending`.
- **RN-075**: El descuento de insumos se realiza al completar la orden (RF-012).
- **RN-076**: Debe mantenerse trazabilidad completa de la operación.

---

## Implementación

**Backend** — `backend/src/routers/production.py` (router registrado en `main.py`):

| Endpoint | Validaciones | Efecto |
|----------|--------------|--------|
| `POST /production/orders/` | Receta existe, no eliminada y `active` (404/400); `quantity_multiplier > 0` (422) | Crea orden en `pending`, calcula `total_yield = yield_quantity × multiplier` en el servidor, registra `created_by`. Retorna 201. |
| `GET /production/orders/` | Filtro opcional `?status=pending\|in_progress\|completed\|cancelled` | Lista órdenes no eliminadas. |
| `GET /production/orders/{id}` | Existe y no eliminada (404) | Detalle de la orden con receta anidada. |
| `PATCH /{id}/start` | Solo desde `pending` (409 si no) | Cambia a `in_progress`, registra `started_at` y auditoría. |
| `PATCH /{id}/cancel` | Solo desde `pending` o `in_progress` (409 si no). Body opcional `{ "reason": "..." }` | Cambia a `cancelled`, registra `cancelled_at`, guarda el motivo en `notes` y auditoría. |

**Cambios de modelo** — migración alembic `c8d41f92ab73`: columnas `started_at` y `cancelled_at` agregadas a `production_orders` para dar trazabilidad al inicio y la cancelación (CA-013.2 y CA-013.4).

**Frontend** — `frontend/src/pages/production/Production.tsx`:

- Tabla de órdenes con estado (Badge), multiplicador, rendimiento total y fecha programada.
- Formulario de registro: receta activa, multiplicador (> 0), fecha programada opcional, notas (máx. 500) y vista previa del rendimiento esperado en vivo.
- Acciones por fila según estado: `pending` → Iniciar / Cancelar; `in_progress` → Cancelar.
- Notificaciones de éxito/error vía toasts (`AlertContext`) y confirmaciones previas (`ConfirmContext`).

**Pendiente**: la finalización con descuento de insumos (`POST /{id}/complete`) corresponde a RF-012 / HU-012.

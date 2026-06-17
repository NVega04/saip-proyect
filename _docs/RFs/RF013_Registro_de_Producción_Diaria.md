# RF-013 — Registro de producción diaria

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-013 |
| **Nombre** | Registro de producción diaria |
| **Módulo** | Producción |
| **Prioridad** | Alta |
| **Estado** | Pendiente |
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
| POST | `/production/orders` | Sí | Crear orden de producción |
| PATCH | `/production/orders/{id}` | Sí | Actualizar estado de orden |

---

## Reglas de negocio

- **RN-073**: La receta debe existir y estar activa.
- **RN-074**: La orden inicia en estado `pending`.
- **RN-075**: El descuento de insumos se realiza al completar la orden (RF-012).
- **RN-076**: Debe mantenerse trazabilidad completa de la operación.

# HU-013 — Registrar producción diaria

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-013 |
| Título | Registrar producción diaria |
| Módulo | Producción |
| Prioridad | Alta |
| Estado | Pendiente |
| RF asociados | RF013 |

---

## Historia

Como encargado de producción, quiero registrar la producción diaria mediante órdenes de producción, para llevar control de los productos elaborados y las materias primas consumidas.

---

## Criterios de aceptación

### CA-013.1 — Creación de orden de producción

**Dado** que accedo al módulo de producción y selecciono "Nueva orden",
**cuando** selecciono una receta existente, ingreso el multiplicador de cantidad (cuántas veces se produce la receta) y la fecha programada,
**entonces** se crea una orden de producción con estado `pending`, se calcula el rendimiento total esperado, y se registra auditoría.

### CA-013.2 — Inicio de producción

**Dado** que existe una orden de producción en estado `pending`,
**cuando** el encargado inicia la producción,
**entonces** el estado de la orden cambia a `in_progress` y se registra la fecha de inicio.

### CA-013.3 — Finalización de producción con descuento de insumos

**Dado** que la producción está en progreso y se completa,
**cuando** el encargado confirma la finalización,
**entonces** el sistema debe:
- Verificar que hay stock suficiente de todos los insumos de la receta
- Descontar las materias primas del inventario
- Incrementar el stock del producto terminado asociado a la receta
- Crear snapshots de inventario por cada insumo (`stock_before`, `stock_after`, `quantity_used`)
- Cambiar el estado a `completed`
- Registrar `completed_at` con la fecha/hora

### CA-013.4 — Cancelación de orden de producción

**Dado** que una orden de producción está en estado `pending` o `in_progress`,
**cuando** el encargado decide cancelarla,
**entonces** el estado cambia a `cancelled`, se registra la fecha y hora de cancelación, y se puede agregar una nota del motivo.

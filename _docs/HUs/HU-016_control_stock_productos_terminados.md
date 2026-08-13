# HU-016 — Control de stock de productos terminados

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-016 |
| Título | Control de stock de productos terminados |
| Módulo | Inventario |
| Prioridad | Alta |
| Estado | Pendiente |
| RF asociados | RF016 |

---

## Historia

Como encargado de inventario, quiero controlar el stock de productos terminados, para conocer las existencias disponibles para la venta y saber cuándo es necesario producir más.

---

## Criterios de aceptación

### CA-016.1 — Actualización automática por producción

**Dado** que se completa una orden de producción asociada a un producto terminado,
**cuando** la orden se marca como `completed`,
**entonces** el `available_quantity` del producto debe incrementarse automáticamente según el rendimiento total de la orden.

### CA-016.2 — Actualización automática por venta

**Dado** que se registra una venta de un producto terminado,
**cuando** la venta se confirma,
**entonces** el `available_quantity` del producto debe disminuirse automáticamente según la cantidad vendida.

### CA-016.3 — Alerta de stock bajo

**Dado** que el `available_quantity` de un producto terminado está por debajo de su `min_stock` configurado,
**cuando** se realiza cualquier operación que afecte el stock,
**entonces** el sistema debe mostrar una alerta visual indicando qué productos requieren reabastecimiento.

### CA-016.4 — Bloqueo temporal de producto

**Dado** que un producto está marcado como `is_locked = true` (bloqueado),
**cuando** se intenta registrar una venta o producción que involucre ese producto,
**entonces** el sistema debe impedir la operación y mostrar un mensaje indicando que el producto está bloqueado.

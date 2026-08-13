# HU-009 — Entrada de insumos al inventario

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-009 |
| Título | Entrada de insumos al inventario |
| Módulo | Inventario |
| Prioridad | Alta |
| Estado | Pendiente |
| RF asociados | RF009 |

---

## Historia

Como encargado de inventario, quiero registrar la entrada de cantidades de insumos al inventario, para mantener actualizado el stock de materias primas.

---

## Criterios de aceptación

### CA-009.1 — Registro de entrada de insumo

**Dado** que selecciono un insumo existente en el inventario,
**cuando** ingreso la cantidad recibida, el proveedor (opcional) y la fecha de recepción,
**entonces** el sistema debe incrementar el `available_quantity` del insumo en la cantidad ingresada, registrar un movimiento de entrada con tipo "entrada", fecha, usuario que realizó la operación, y mostrar mensaje de éxito.

### CA-009.2 — Validación de cantidad positiva

**Dado** que ingreso una cantidad inválida (cero, negativa o no numérica),
**cuando** intento guardar el registro,
**entonces** el sistema debe impedir la operación y mostrar un mensaje de error específico.

### CA-009.3 — Historial de movimientos

**Dado** que se registra una entrada de insumo,
**cuando** la operación se completa,
**entonces** se debe crear un registro en el historial de movimientos de inventario con tipo de movimiento, insumo, cantidad, usuario, fecha y proveedor asociado.

### CA-009.4 — Notificación de stock mínimo

**Dado** que después de una entrada el stock del insumo supera el `max_stock` configurado,
**cuando** se completa el registro,
**entonces** el sistema debe mostrar una advertencia opcional (no bloqueante) indicando que se ha superado el stock máximo sugerido.

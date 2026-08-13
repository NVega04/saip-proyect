# HU-010 — Control de salidas de inventario

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-010 |
| Título | Control de salidas de inventario |
| Módulo | Inventario |
| Prioridad | Alta |
| Estado | Pendiente |
| RF asociados | RF010 |

---

## Historia

Como encargado de inventario, quiero registrar salidas de insumos del inventario, para reflejar el consumo real de materias primas.

---

## Criterios de aceptación

### CA-010.1 — Registro de salida de insumo

**Dado** que selecciono un insumo con stock disponible,
**cuando** registro una cantidad de salida válida (positiva y menor o igual al stock actual),
**entonces** el sistema debe descontar la cantidad del `available_quantity` del insumo, registrar un movimiento de salida con tipo "salida", fecha y usuario, y mostrar mensaje de éxito.

### CA-010.2 — Control de stock insuficiente

**Dado** que el stock disponible (`available_quantity`) es menor que la cantidad solicitada para la salida,
**cuando** intento registrar la salida,
**entonces** el sistema debe bloquear la operación y mostrar un mensaje de error indicando que no hay suficiente stock disponible.

### CA-010.3 — Justificación de salida

**Dado** que registro una salida de inventario,
**cuando** completo el registro,
**entonces** debo poder especificar el motivo de la salida (producción, merma, ajuste, etc.) y agregar notas u observaciones.

### CA-010.4 — Notificación de stock mínimo

**Dado** que después de una salida el stock del insumo queda por debajo del `min_stock` configurado,
**cuando** se completa el registro,
**entonces** el sistema debe mostrar una alerta (no bloqueante) indicando que el insumo está por debajo del stock mínimo sugerido.

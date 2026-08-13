# HU-012 — Descontar materias primas al producir

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-012 |
| Título | Descontar materias primas al producir |
| Módulo | Producción |
| Prioridad | Alta |
| Estado | Pendiente |
| RF asociados | RF012 |

---

## Historia

Como encargado de producción, quiero que el sistema descuente automáticamente las materias primas del inventario al confirmar una orden de producción basada en una receta, para mantener el stock actualizado sin intervención manual.

---

## Criterios de aceptación

### CA-012.1 — Descuento automático al producir

**Dado** que registro una orden de producción basada en una receta con ingredientes definidos,
**cuando** confirmo la producción con un multiplicador de cantidad,
**entonces** el sistema debe calcular las cantidades de cada insumo requerido (cantidad de receta × multiplicador), verificar que haya stock suficiente de cada uno, y descontar las cantidades del `available_quantity` de cada insumo.

### CA-012.2 — Validación de stock insuficiente

**Dado** que no hay suficiente stock de al menos un insumo necesario para la producción,
**cuando** intento confirmar la orden de producción,
**entonces** el sistema debe identificar qué insumos tienen stock insuficiente, mostrar un mensaje detallado y bloquear la operación.

### CA-012.3 — Captura de snapshot de inventario

**Dado** que se confirma una orden de producción,
**cuando** se descuentan los insumos,
**entonces** el sistema debe crear un snapshot (`ProductionOrderSnapshot`) por cada insumo, registrando `stock_before`, `stock_after` y `quantity_used` para mantener trazabilidad del consumo.

### CA-012.4 — Registro de auditoría

**Dado** que se completa una orden de producción,
**cuando** se descuentan las materias primas,
**entonces** se registra quién realizó la producción (`created_by`), la fecha y hora, y se actualiza el estado de la orden a `completed`.

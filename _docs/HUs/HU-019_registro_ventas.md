# HU-019 — Registro de ventas de productos

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-019 |
| Título | Registro de ventas de productos |
| Módulo | Ventas |
| Prioridad | Alta |
| Estado | Pendiente |
| RF asociados | RF019 |

---

## Historia

Como encargado de ventas, quiero registrar la venta de productos (comerciales y producidos internamente), para descontar automáticamente el inventario correspondiente, llevar control comercial y generar el historial de ventas.

---

## Criterios de aceptación

### CA-019.1 — Registro de venta con selección de productos

**Dado** que accedo al módulo de ventas y selecciono la opción "Nueva venta",
**cuando** agrego productos al carrito seleccionando del listado de productos disponibles (tanto productos de producción propia como comerciales),
**entonces** puedo especificar la cantidad de cada producto, y el sistema calcula el subtotal por producto y el total de la venta.

### CA-019.2 — Validación de stock al vender

**Dado** que intento agregar un producto al carrito con una cantidad mayor al `available_quantity` del producto,
**cuando** confirmo la venta,
**entonces** el sistema debe mostrar un mensaje de error indicando qué productos no tienen suficiente stock y cuánto hay disponible, impidiendo la operación.

### CA-019.3 — Descuento automático de inventario

**Dado** que se confirma una venta exitosamente,
**cuando** la venta se registra,
**entonces** el sistema debe:
- Descontar del `available_quantity` de cada producto vendido
- Si el producto es de producción propia, descontar del producto correspondiente
- Si el producto es comercial, descontar del `CommercialProduct` correspondiente
- Registrar el total de la venta y el método de pago

### CA-019.4 — Historial de ventas

**Dado** que se ha registrado una venta,
**cuando** accedo al módulo de historial de ventas,
**entonces** puedo consultar las ventas realizadas con filtros por fecha, producto, rango de precios, y ver detalles de cada venta (productos, cantidades, total, fecha, usuario que registró).

### CA-019.5 — Anulación de venta

**Dado** que se necesita anular una venta registrada,
**cuando** el administrador confirma la anulación,
**entonces** el sistema debe revertir los descuentos de inventario realizados por esa venta y marcarla como anulada en el historial, manteniendo la trazabilidad.

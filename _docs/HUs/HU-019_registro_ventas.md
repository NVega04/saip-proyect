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

Como encargado de ventas, quiero registrar la venta de productos, para descontar automáticamente el inventario y llevar control comercial.

---

## Criterios de aceptación

### CA-019.1 — Registro exitoso
**Dado** que selecciono productos y cantidades válidas,  
**cuando** confirmo la venta,  
**entonces** el sistema debe registrar la venta y descontar el stock correspondiente.

### CA-019.2 — Validación de stock
**Dado** que no hay suficiente inventario,  
**cuando** intento registrar la venta,  
**entonces** el sistema debe impedir la operación.
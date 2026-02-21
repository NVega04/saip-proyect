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

Como encargado de inventario, quiero registrar salidas de insumos, para reflejar el consumo real.

---

## Criterios de aceptación

### CA-010.1 — Registro de salida
**Dado** que selecciono un insumo,  
**cuando** registro una cantidad de salida válida,  
**entonces** el sistema debe descontarla del stock.

### CA-010.2 — Control de stock insuficiente
**Dado** que el stock disponible es menor que la cantidad solicitada,  
**cuando** intento registrar la salida,  
**entonces** el sistema debe bloquear la operación.
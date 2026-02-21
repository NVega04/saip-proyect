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

Como encargado de inventario, quiero registrar la entrada de cantidades de insumos, para mantener actualizado el stock.

---

## Criterios de aceptación

### CA-009.1 — Registro de entrada
**Dado** que selecciono un insumo existente,  
**cuando** ingreso la cantidad recibida y confirmo,  
**entonces** el stock debe incrementarse correctamente.

### CA-009.2 — Validación de cantidad
**Dado** que ingreso una cantidad inválida o negativa,  
**cuando** intento guardar el registro,  
**entonces** el sistema debe impedir la operación.
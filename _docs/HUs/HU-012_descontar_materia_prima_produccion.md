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

Como encargado de producción, quiero que el sistema descuente automáticamente las materias primas utilizadas, para mantener el inventario actualizado.

---

## Criterios de aceptación

### CA-012.1 — Descuento automático
**Dado** que registro una producción basada en una receta,  
**cuando** confirmo la producción,  
**entonces** el sistema debe descontar las materias primas correspondientes.

### CA-012.2 — Validación de stock
**Dado** que no hay suficiente materia prima,  
**cuando** intento registrar la producción,  
**entonces** el sistema debe impedir el proceso.
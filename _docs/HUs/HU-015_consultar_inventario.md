# HU-015 — Consulta general de inventario

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-015 |
| Título | Consulta general de inventario |
| Módulo | Inventario |
| Prioridad | Alta |
| Estado | Pendiente |
| RF asociados | RF015 |

---

## Historia

Como usuario con permisos en el módulo de inventario, quiero consultar un consolidado visual de insumos, productos terminados y productos comerciales que indique cuáles están en bajo stock o sobre stock, para tener una idea general del estado del inventario y descargar un informe con los filtros aplicados.

---

## Criterios de aceptación

### CA-015.1 — Consolidado de inventario

**Dado** que tengo acceso al módulo de inventario,
**cuando** ingreso a la vista de inventario (`/inventario`),
**entonces** veo el listado consolidado de insumos, productos terminados y productos comerciales con su stock disponible, mínimo y máximo.

### CA-015.2 — Indicadores de stock

**Dado** el consolidado de inventario,
**cuando** un ítem tiene `available_quantity <= min_stock`,
**entonces** se muestra marcado como **bajo stock**; y cuando supera `max_stock`, se muestra como **sobre stock**.

### CA-015.3 — Filtros y paginación

**Dado** el consolidado de inventario,
**cuando** aplico filtros (tipo de ítem, estado de stock, categoría, búsqueda) o navego entre páginas,
**entonces** la vista se actualiza mostrando únicamente los resultados correspondientes.

### CA-015.4 — Descarga de informe

**Dado** el consolidado de inventario con filtros aplicados,
**cuando** solicito descargar el informe,
**entonces** se genera un archivo Excel con exactamente los mismos filtros.

### CA-015.5 — Restricción de acceso

**Dado** que no tengo asignado el módulo `inventory`,
**cuando** intento acceder a la vista de inventario,
**entonces** el sistema me redirige al dashboard.
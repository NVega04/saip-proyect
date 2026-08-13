# HU-008 — Consulta de insumos

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-008 |
| Título | Consulta de insumos |
| Módulo | Insumos |
| Prioridad | Alta |
| Estado | Completado |
| RF asociados | RF008 |

---

## Historia

Como usuario con permisos en el módulo de insumos, quiero consultar la lista de insumos disponibles, para conocer el estado del inventario de materias primas.

---

## Criterios de aceptación

### CA-008.1 — Visualización de listado

**Dado** que accedo al módulo de insumos,
**cuando** se carga la página,
**entonces** visualizo una tabla con todos los insumos registrados incluyendo columnas: nombre, categoría, unidad de medida, cantidad disponible, stock mínimo, stock máximo, estado y acciones disponibles (editar, eliminar).

### CA-008.2 — Búsqueda y paginación

**Dado** que hay muchos insumos registrados,
**cuando** uso la barra de búsqueda,
**entonces** puedo filtrar los insumos por nombre; y los resultados se muestran paginados para facilitar la navegación.

### CA-008.3 — Detalle del insumo

**Dado** que selecciono un insumo de la lista,
**cuando** accedo a su detalle,
**entonces** puedo ver la información completa: nombre, descripción, categoría, unidad, cantidades de stock, proveedor asociado, fecha de vencimiento, fechas de auditoría.

### CA-008.4 — Edición y eliminación

**Dado** que visualizo la lista de insumos,
**cuando** selecciono las opciones de editar o eliminar,
**entonces** puedo modificar los campos del insumo o realizar eliminación lógica (soft delete), con la correspondiente confirmación y registro de auditoría.

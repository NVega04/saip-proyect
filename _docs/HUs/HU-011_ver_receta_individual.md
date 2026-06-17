# HU-011 — Ver receta individual

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-011 |
| Título | Ver receta individual |
| Módulo | Recetas |
| Prioridad | Alta |
| Estado | Completado |
| RF asociados | RF011 |

---

## Historia

Como usuario con permisos en el módulo de recetas, quiero consultar una receta específica con todos sus detalles, para conocer los insumos, cantidades requeridas y el producto asociado.

---

## Criterios de aceptación

### CA-011.1 — Visualización de receta con ingredientes

**Dado** que selecciono una receta de la lista,
**cuando** accedo a su vista de detalle,
**entonces** visualizo: nombre de la receta, descripción, producto asociado (si tiene), cantidad de rendimiento y su unidad, estado (activo/inactivo), y una tabla con todos los ingredientes asociados (insumo, cantidad, unidad, notas).

### CA-011.2 — Información de cada ingrediente

**Dado** que veo el detalle de una receta,
**cuando** consulto los ingredientes,
**entonces** cada ingrediente muestra: nombre del insumo, cantidad requerida, unidad de medida y notas opcionales.

### CA-011.3 — Producto asociado a la receta

**Dado** que la receta está asociada a un producto terminado,
**cuando** veo el detalle,
**entonces** puedo ver qué producto produce esta receta, incluyendo su nombre y unidad.

### CA-011.4 — Edición desde el detalle

**Dado** que visualizo una receta,
**cuando** tengo permisos suficientes,
**entonces** puedo acceder a las opciones de editar la receta o sus ingredientes directamente desde la vista de detalle.

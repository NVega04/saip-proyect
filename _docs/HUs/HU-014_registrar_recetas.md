# HU-014 — Registrar recetas de productos

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-014 |
| Título | Registrar recetas de productos |
| Módulo | Recetas |
| Prioridad | Alta |
| Estado | Completado |
| RF asociados | RF014 |

---

## Historia

Como usuario con permisos en el módulo de recetas, quiero registrar recetas de productos con sus ingredientes y cantidades, para definir los insumos necesarios en producción.

---

## Criterios de aceptación

### CA-014.1 — Creación de receta con ingredientes

**Dado** que accedo al módulo de recetas y selecciono "Nueva receta",
**cuando** completo el formulario con nombre, descripción opcional, producto asociado opcional, cantidad de rendimiento y su unidad,
**entonces** la receta se almacena con estado `active`, se registra auditoría, y se muestra mensaje de éxito.

### CA-014.2 — Asociación de ingredientes en la creación

**Dado** que estoy creando una receta,
**cuando** agrego ingredientes (insumo, cantidad, unidad, notas opcionales),
**entonces** cada ingrediente se asocia a la receta y se almacena en la tabla `recipe_ingredients` con el orden y cantidades definidos.

### CA-014.3 — Actualización de receta (reemplazo de ingredientes)

**Dado** que edito una receta existente,
**cuando** modifico los ingredientes (agrego, elimino o cambio cantidades),
**entonces** el sistema reemplaza completamente la lista de ingredientes anteriores por la nueva, manteniendo la auditoría de la receta.

### CA-014.4 — Producto asociado opcional

**Dado** que creo o edito una receta,
**cuando** decido asociarla a un producto terminado,
**entonces** puedo seleccionar un producto existente del listado; si no asocio ninguno, el campo queda vacío y la receta se guarda igualmente.

### CA-014.5 — Validación de datos

**Dado** que intento crear una receta con datos inválidos (nombre vacío, ingredientes sin cantidad, unidad inexistente),
**cuando** intento guardar,
**entonces** el sistema muestra errores de validación específicos por campo.

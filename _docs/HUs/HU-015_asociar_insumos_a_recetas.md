# HU-015 — Asociación de insumos a recetas

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-015 |
| Título | Asociación de insumos a recetas |
| Módulo | Recetas |
| Prioridad | Alta |
| Estado | Completado |
| RF asociados | RF015 |

---

## Historia

Como usuario con permisos en el módulo de recetas, quiero asociar insumos a recetas con sus cantidades y unidades específicas, para que el sistema pueda calcular los materiales necesarios al momento de producir.

---

## Criterios de aceptación

### CA-015.1 — Asociación de insumo a receta

**Dado** que estoy editando una receta existente,
**cuando** agrego un insumo seleccionándolo del listado de insumos disponibles,
**entonces** el insumo se asocia a la receta y puedo definir la cantidad requerida, la unidad de medida y notas opcionales.

### CA-015.2 — Edición de cantidades y unidades

**Dado** que un insumo ya está asociado a una receta,
**cuando** modifico su cantidad o unidad de medida,
**entonces** los cambios se actualizan en la tabla `recipe_ingredients` y se reflejan al consultar la receta.

### CA-015.3 — Eliminación de insumo de una receta

**Dado** que un insumo ya no es necesario en una receta,
**cuando** lo elimino de la lista de ingredientes,
**entonces** el sistema elimina el registro de `recipe_ingredients` correspondiente y actualiza la lista.

### CA-015.4 — Validación de datos del ingrediente

**Dado** que intento asociar un insumo sin especificar cantidad o con cantidad cero,
**cuando** intento guardar el ingrediente,
**entonces** el sistema muestra un error de validación y no permite la asociación.

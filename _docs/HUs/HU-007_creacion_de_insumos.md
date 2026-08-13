# HU-007 — Creación de insumos

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-007 |
| Título | Creación de insumos |
| Módulo | Insumos |
| Prioridad | Alta |
| Estado | Completado |
| RF asociados | RF007 |

---

## Historia

Como usuario con permisos en el módulo de insumos, quiero registrar materias primas en el sistema, para gestionar su stock, asignarlas a recetas y controlar su inventario.

---

## Criterios de aceptación

### CA-007.1 — Registro exitoso de insumo

**Dado** que accedo al módulo de insumos y selecciono la opción "Nuevo insumo",
**cuando** completo el formulario con datos válidos (nombre único, categoría, unidad de medida, stock inicial, stock mínimo y máximo, proveedor opcional, fecha de vencimiento opcional),
**entonces** el insumo se almacena correctamente en la base de datos con estado `active`, se registra auditoría (`created_by`, `created_at`) y se muestra mensaje de éxito.

### CA-007.2 — Validación de unicidad de nombre

**Dado** que intento crear un insumo con un nombre que ya existe en el sistema,
**cuando** intento guardar el registro,
**entonces** el sistema muestra un mensaje de error indicando que el nombre ya está registrado.

### CA-007.3 — Asignación de categoría y unidad

**Dado** que estoy creando un insumo,
**cuando** selecciono la categoría y la unidad de medida,
**entonces** ambas son obligatorias y debo seleccionarlas de listas precargadas de categorías de insumos y unidades de medida existentes.

### CA-007.4 — Campos de control de stock

**Dado** que estoy creando un insumo,
**cuando** ingreso los valores de stock,
**entonces** puedo definir `available_quantity` (cantidad inicial), `min_stock` (stock mínimo de alerta) y `max_stock` (stock máximo), todos con valores numéricos predeterminados en 0.

### CA-007.5 — Proveedor asociado

**Dado** que el insumo tiene un proveedor habitual,
**cuando** lo creo,
**entonces** puedo asociarlo opcionalmente a un usuario registrado como proveedor (`supplier_id`), para registrar quién provee ese insumo.

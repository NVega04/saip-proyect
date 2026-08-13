# RF-015 — Asociación de Inventario de Insumos con Recetas

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-015 |
| **Nombre** | Asociación de inventario de insumos con recetas |
| **Módulo** | Recetas |
| **Prioridad** | Alta |
| **Estado** | Implementado |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe permitir asociar insumos (materias primas) registrados en el catálogo a las recetas, definiendo cantidades, unidades de medida y notas opcionales. Esta asociación se gestiona dentro del CRUD de recetas mediante ingredientes anidados.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `recipe_id` | Entero | Sí | Debe existir en `recipes` |
| `supply_id` | Entero | Sí | Debe existir en `supplies` |
| `quantity` | Decimal | Sí | Mayor a 0 |
| `unit_id` | Entero | Sí | Debe existir en `units` |
| `notes` | Texto | No | Máximo 255 caracteres |

---

## Proceso

1. El usuario accede a la edición de una receta existente.
2. Agrega un insumo seleccionándolo del listado de insumos disponibles.
3. Ingresa cantidad requerida, unidad de medida y notas opcionales.
4. Frontend envía `PATCH /recipes/{id}` con la lista completa de ingredientes.
5. Backend reemplaza los ingredientes anteriores por los nuevos.
6. Se registra auditoría.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Asociación guardada | 200 | Datos de la receta actualizada |
| Insumo no encontrado | 404 | Recurso no encontrado |
| Datos inválidos | 422 | Detalle de errores |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| PATCH | `/recipes/{id}` | Sí | Actualizar receta (reemplaza ingredientes) |

---

## Reglas de negocio

- **RN-047**: No se permite asociar el mismo insumo más de una vez en la misma receta (se reemplaza la lista completa).
- **RN-048**: Solo pueden asociarse insumos existentes y activos.
- **RN-049**: La unidad de medida debe existir en el catálogo de unidades.
- **RN-050**: Toda modificación de ingredientes se registra en auditoría.

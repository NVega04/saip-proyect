# RF-011 — Ver receta individual

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-011 |
| **Nombre** | Ver receta individual |
| **Módulo** | Recetas |
| **Prioridad** | Alta |
| **Estado** | Implementado |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe permitir a los usuarios consultar el detalle completo de una receta específica, incluyendo nombre, descripción, producto asociado, rendimiento, y lista de ingredientes con cantidades y unidades.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `recipe_id` | Entero | Sí | Debe existir y estar activo en el sistema |

---

## Proceso

1. El usuario accede al módulo de recetas (`/recetas`) y visualiza el listado.
2. Selecciona una receta para ver su detalle.
3. El sistema consulta `GET /recipes/{id}` que retorna la receta con ingredientes.
4. Se muestra: nombre, descripción, producto asociado (si tiene), cantidad de rendimiento, unidad, estado, y tabla de ingredientes (insumo, cantidad, unidad, notas).
5. La vista permite editar la receta o sus ingredientes si se tienen permisos.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Consulta exitosa | 200 | Datos completos de la receta con ingredientes |
| Receta no encontrada | 404 | Recurso no encontrado |
| No autenticado | 401 | Token inválido |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| GET | `/recipes/` | Sí | Listar recetas |
| GET | `/recipes/{id}` | Sí | Obtener receta con ingredientes |

---

## Reglas de negocio

- **RN-040**: Solo usuarios autenticados pueden visualizar recetas.
- **RN-041**: La información es de consulta; permite edición si se tienen permisos.
- **RN-042**: No se muestran recetas eliminadas (soft delete).

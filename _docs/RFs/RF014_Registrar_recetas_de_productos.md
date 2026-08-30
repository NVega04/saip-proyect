# RF-014 — Registrar recetas de productos

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-014 |
| **Nombre** | Registrar recetas de productos |
| **Módulo** | Recetas |
| **Prioridad** | Alta |
| **Estado** | Implementado |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe permitir registrar recetas de productos con su lista de ingredientes (insumos, cantidades y unidades). Cada receta se asocia obligatoriamente a un producto terminado y define un rendimiento con su unidad de medida.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `name` | Texto | Sí | Máximo 150 caracteres |
| `description` | Texto | No | Máximo 500 caracteres |
| `product_id` | Entero | Sí | Debe existir en `products` |
| `yield_quantity` | Decimal | Sí | Por defecto 1 |
| `yield_unit_id` | Entero | Sí | Debe existir en `units` |
| `ingredients` | Lista | Sí | Arreglo de `{ supply_id, quantity, unit_id, notes }` |

---

## Proceso

1. El usuario accede al módulo de recetas (`/recetas`) y selecciona "Nueva receta".
2. Completa el formulario con nombre, descripción, producto asociado (opcional), rendimiento.
3. Agrega ingredientes seleccionando insumos del catálogo, con cantidad y unidad.
4. Frontend envía `POST /recipes/` con JWT.
5. Backend valida datos, crea la receta y sus ingredientes en `recipe_ingredients`.
6. Se registra auditoría.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Receta creada | 201 | Datos de la receta con ingredientes |
| Datos inválidos | 422 | Detalle de errores |
| No autenticado | 401 | Token inválido |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| GET | `/recipes/` | Sí | Listar recetas |
| GET | `/recipes/{id}` | Sí | Obtener receta con ingredientes |
| POST | `/recipes/` | Sí | Crear receta con ingredientes |
| PATCH | `/recipes/{id}` | Sí | Actualizar receta (reemplaza ingredientes) |
| DELETE | `/recipes/{id}` | Sí | Eliminación lógica de receta |

---

## Reglas de negocio

- **RN-043**: La receta debe tener al menos un ingrediente para poder crearse.
- **RN-044**: Al actualizar una receta, los ingredientes se reemplazan completamente.
- **RN-045**: La asociación con producto terminado es obligatoria; no puede desvincularse posteriormente (PATCH con `product_id: null` responde 400).
- **RN-046**: Toda creación/actualización se registra en auditoría.

---

## Implementación

**Producto terminado obligatorio + creación inline**: el formulario de recetas exige seleccionar el producto terminado (crear y editar) y ofrece un botón "Crear producto" que abre un mini-modal para registrar el producto (nombre, unidad, descripción) sin salir de la página; al crearlo queda autoseleccionado en la receta. El backend valida la existencia del producto en `POST /recipes/` (requerido) y rechaza desvincularlo vía `PATCH`. Al completar una orden de producción, el rendimiento se suma al stock del producto vinculado (ver RF-012).

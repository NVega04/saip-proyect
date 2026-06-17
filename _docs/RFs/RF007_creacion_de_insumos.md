# RF-007 — Creación de insumos

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-007 |
| **Nombre** | Creación de insumos |
| **Módulo** | Insumos |
| **Prioridad** | Alta |
| **Estado** | Implementado |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe permitir registrar nuevos insumos (materias primas) en el catálogo, con su nombre único, categoría, unidad de medida, cantidades de stock, proveedor opcional y fecha de vencimiento opcional.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `name` | Texto | Sí | Máximo 150 caracteres, único en el sistema |
| `description` | Texto | No | Máximo 500 caracteres |
| `category_id` | Entero | Sí | Debe existir en `supply_categories` |
| `unit_id` | Entero | Sí | Debe existir en `units` |
| `available_quantity` | Decimal | No | Por defecto 0 |
| `min_stock` | Decimal | No | Por defecto 0 |
| `max_stock` | Decimal | No | Por defecto 0 |
| `supplier_id` | Entero | No | Debe existir en `users` (opcional) |
| `expiration_date` | Fecha | No | Opcional |

---

## Proceso

1. El usuario accede al módulo de insumos (`/supplies`) y selecciona "Nuevo insumo".
2. Completa el formulario con los datos requeridos.
3. Frontend envía `POST /supplies/` con JWT en header `session-token`.
4. Backend valida datos, verifica unicidad de nombre, crea el insumo con estado `active`.
5. Se registra auditoría (`created_by`, `created_at`).
6. Muestra mensaje de éxito y redirige a la lista.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Insumo creado | 201 | Datos del insumo creado |
| Nombre duplicado | 400 | Error de unicidad |
| Datos inválidos | 422 | Detalle de errores |
| No autenticado | 401 | Token inválido |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| GET | `/supplies/` | Sí | Listar insumos |
| GET | `/supplies/{id}` | Sí | Obtener insumo por ID |
| POST | `/supplies/` | Sí | Crear insumo |
| PUT | `/supplies/{id}` | Sí | Actualizar insumo |
| DELETE | `/supplies/{id}` | Sí | Eliminación lógica de insumo |

---

## Reglas de negocio

- **RN-033**: El nombre del insumo debe ser único en el sistema.
- **RN-034**: Categoría y unidad de medida son obligatorias.
- **RN-035**: Todo insumo creado se registra en auditoría.
- **RN-036**: La eliminación es lógica (soft delete).

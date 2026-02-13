# RF-008 — Consulta de insumos en el inventario

---

## Identificación

| Campo | Valor |
|------|-------|
| ID | RF-008 |
| Nombre | Consulta de insumos en el inventario |
| Módulo | Inventario |
| Prioridad | Alta |
| Estado | Pendiente |
| Fecha | Febrero 2026 |

---

## Descripción

El sistema debe permitir consultar el catálogo de insumos registrados en el inventario, mostrando su información general y su stock disponible actualizado.  
La consulta debe permitir filtros por nombre, categoría y proveedor para facilitar la gestión y control del inventario.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|------|------|-------------|--------------|
| search | Texto | No | Puede ser vacío |
| categoria | Texto | No | Si se envía, debe existir |
| proveedor | Texto | No | Si se envía, debe existir |
| page | Entero | No | Debe ser >= 1 |
| limit | Entero | No | Debe estar entre 1 y 100 |

---

## Proceso

1. El usuario autenticado ingresa al módulo de inventario.
2. Selecciona la opción **Consultar insumos**.
3. El sistema carga el listado de insumos registrados.
4. El usuario puede buscar por nombre o filtrar por categoría y proveedor.
5. El sistema valida los filtros enviados.
6. El sistema consulta la base de datos y obtiene los resultados.
7. El sistema muestra el listado con el stock actual de cada insumo.
8. El usuario puede seleccionar un insumo para ver detalles adicionales.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|----------|------------|----------|
| Consulta exitosa | 200 | `{ "items": [...] }` |
| Sin resultados | 200 | `{ "items": [] }` |
| Filtros inválidos | 422 | Detalle de errores de validación |
| No autorizado | 403 | `{ "message": "Forbidden" }` |

---

## Endpoint asociado

| Método | Ruta | Auth requerida |
|--------|------|---------------|
| GET | `/api/v1/inventory/items` | Sí |

---

## Reglas de negocio

- **RN-020:** Solo usuarios autenticados pueden consultar el inventario.
- **RN-021:** El stock mostrado debe reflejar el valor actualizado más reciente.
- **RN-022:** El sistema debe permitir búsqueda y filtros por categoría/proveedor.
- **RN-023:** La consulta no debe permitir modificación de datos (solo lectura).
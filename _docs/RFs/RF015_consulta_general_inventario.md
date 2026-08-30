# RF-015 — Consulta general de inventario

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-015 |
| **Nombre** | Consulta general de inventario (consolidado visual) |
| **Módulo** | Inventario |
| **Prioridad** | Alta |
| **Estado** | Pendiente |
| **Fecha** | Agosto 2026 |

---

## Descripción

El sistema debe ofrecer una vista visual consolidada del inventario para consulta general de **insumos**, **productos terminados** y **productos comerciales**. La vista debe indicar el estado de stock de cada ítem (bajo stock o sobre stock) para que el usuario tenga una idea general de la situación del inventario, y debe permitir descargar un informe (Excel) acorde a los filtros aplicados.

---

## Entradas (filtros de consulta)

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `item_type` | Enum | No | `supply`, `product`, `commercial` (vacío = todos) |
| `stock_status` | Enum | No | `bajo`, `normal`, `sobre` (vacío = todos) |
| `category_id` | Entero | No | Debe existir en la categoría correspondiente al tipo |
| `search` | Texto | No | Búsqueda por nombre (máximo 150 caracteres) |
| `status` | Enum | No | `active`, `inactive` (por defecto `active`) |
| `page` | Entero | No | Por defecto 1 |
| `limit` | Entero | No | Por defecto 10 |

---

## Proceso

1. El usuario accede al módulo Inventario (`/inventario`).
2. El frontend solicita `GET /inventory/summary` con los filtros seleccionados.
3. El backend consolida las tablas `products`, `supplies` y `commercial_products` (activos y no eliminados), resolviendo unidad de medida y categoría.
4. El backend calcula el estado de stock de cada ítem:
   - **Bajo stock**: `available_quantity <= min_stock`
   - **Sobre stock**: `available_quantity > max_stock`
   - **Normal**: caso contrario
5. El backend retorna los ítems paginados y un resumen con totales (total de ítems, bajo stock, sobre stock).
6. Si el usuario solicita el informe, el frontend descarga `GET /inventory/report` con los mismos filtros y el backend genera un Excel con la paleta SAIP.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Consulta exitosa | 200 | `{ items, total, page, limit, summary: { total_items, bajo_stock, sobre_stock } }` |
| Informe generado | 200 | Archivo `.xlsx` (StreamingResponse) |
| No autenticado | 401 | Token inválido |
| Sin permiso de módulo | 403 | Acceso denegado |
| Filtros inválidos | 422 | Detalle de errores |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| GET | `/inventory/summary` | Sí | Consulta consolidada de inventario con filtros y paginación |
| GET | `/inventory/report` | Sí | Informe Excel con los filtros aplicados |

---

## Reglas de negocio

- **RN-082**: Se considera bajo stock cuando `available_quantity <= min_stock`.
- **RN-083**: Se considera sobre stock cuando `available_quantity > max_stock`.
- **RN-084**: Solo se incluyen ítems activos y no eliminados (`deleted_at IS NULL`).
- **RN-085**: El informe respeta exactamente los filtros aplicados en la consulta.
- **RN-086**: El acceso al módulo se restringe por módulo `inventory` en los roles.
# RF-008 — Consulta de insumos en el inventario

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-008 |
| **Nombre** | Consulta de insumos en el inventario |
| **Módulo** | Insumos |
| **Prioridad** | Alta |
| **Estado** | Implementado |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe permitir consultar el catálogo de insumos registrados, con búsqueda por nombre, paginación, y visualización del detalle completo de cada insumo.

---

## Entradas (parámetros de consulta)

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| (parámetros de búsqueda) | - | No | Búsqueda local por nombre en frontend |

---

## Proceso

1. El usuario autenticado ingresa al módulo de insumos (`/supplies`).
2. El sistema carga la lista completa de insumos desde `GET /supplies/`.
3. La interfaz muestra una tabla con columnas: nombre, categoría, unidad, cantidad disponible, stock mínimo, stock máximo, estado, acciones.
4. El usuario puede buscar por nombre mediante la barra de búsqueda (filtro local).
5. Los resultados se muestran paginados.
6. El usuario puede seleccionar un insumo para ver o editar su detalle.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Consulta exitosa | 200 | Lista de insumos |
| Sin resultados | 200 | Lista vacía |
| No autenticado | 401 | Token inválido |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| GET | `/supplies/` | Sí | Listar insumos |
| GET | `/supplies/{id}` | Sí | Obtener detalle de insumo |

---

## Reglas de negocio

- **RN-037**: Solo usuarios autenticados pueden consultar insumos.
- **RN-038**: El stock mostrado refleja el valor actualizado más reciente.
- **RN-039**: La consulta es de solo lectura; no permite modificación directa.

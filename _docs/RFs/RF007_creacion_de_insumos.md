# RF-007 — Creación de insumos

---

## Identificación

| Campo | Valor |
|------|-------|
| ID | RF-007 |
| Nombre | Creación de insumos |
| Módulo | Inventario |
| Prioridad | Alta |
| Estado | Pendiente |
| Fecha | Febrero 2026 |

---

## Descripción

El sistema debe permitir registrar nuevos insumos en el catálogo de inventario, almacenando su información básica como nombre, descripción, categoría y unidad de medida.  
El insumo creado debe quedar disponible para su uso en operaciones futuras como entradas, salidas y consultas de inventario.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|------|------|-------------|--------------|
| nombre | Texto | Sí | No vacío, mínimo 3 caracteres |
| descripcion | Texto | No | Máximo 255 caracteres |
| categoria | Texto | Sí | No vacío |
| unidad_medida | Texto | Sí | No vacío |
| proveedor | Texto | No | Opcional |
| stock_inicial | Entero | Sí | Debe ser >= 0 |

---

## Proceso

1. El usuario autorizado ingresa al módulo de inventario.
2. Selecciona la opción **Crear insumo**.
3. El usuario ingresa la información requerida del insumo.
4. El sistema valida los campos obligatorios.
5. El sistema verifica que no exista un insumo registrado con el mismo nombre.
6. El sistema genera un identificador único para el insumo.
7. El sistema registra el insumo en la base de datos.
8. El sistema registra auditoría de creación (fecha, hora y responsable).
9. El sistema muestra mensaje de confirmación y el insumo aparece en el catálogo.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|----------|------------|----------|
| Insumo creado correctamente | 201 | `{ "message": "Item created successfully", "item_id": "..." }` |
| Insumo duplicado | 409 | `{ "message": "Item already exists" }` |
| Datos inválidos | 422 | Detalle de errores de validación |
| No autorizado | 403 | `{ "message": "Forbidden" }` |

---

## Endpoint asociado

| Método | Ruta | Auth requerida |
|--------|------|---------------|
| POST | `/api/v1/inventory/items` | Sí |

---

## Reglas de negocio

- **RN-015:** Solo usuarios con rol **Administrador** o **Inventario** pueden registrar insumos.
- **RN-016:** No se permite registrar insumos con nombre duplicado.
- **RN-017:** El stock inicial debe ser mayor o igual a cero.
- **RN-018:** Todo insumo debe tener categoría y unidad de medida obligatoria.
- **RN-019:** Toda creación de insumo debe registrarse en auditoría.
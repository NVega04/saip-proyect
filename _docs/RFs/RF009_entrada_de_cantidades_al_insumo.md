# RF-009 — Entrada de cantidades de insumo al inventario

---

## Identificación

| Campo | Valor |
|------|-------|
| ID | RF-009 |
| Nombre | Entrada de cantidades de insumo al inventario |
| Módulo | Inventario |
| Prioridad | Alta |
| Estado | Pendiente |
| Fecha | Febrero 2026 |

---

## Descripción

El sistema debe permitir registrar entradas de insumos al inventario, incrementando automáticamente el stock disponible del insumo seleccionado.  
Cada entrada debe quedar registrada como movimiento para control histórico y auditoría.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|------|------|-------------|--------------|
| item_id | UUID / Int | Sí | Debe existir en base de datos |
| cantidad | Entero | Sí | Debe ser > 0 |
| proveedor | Texto | No | Opcional |
| observacion | Texto | No | Máximo 255 caracteres |

---

## Proceso

1. El usuario autorizado ingresa al módulo de inventario.
2. Selecciona la opción **Registrar entrada**.
3. El usuario selecciona el insumo al cual se le hará la entrada.
4. El usuario ingresa la cantidad recibida.
5. El sistema valida que el insumo exista.
6. El sistema valida que la cantidad sea mayor a cero.
7. El sistema registra el movimiento de entrada en la base de datos.
8. El sistema incrementa automáticamente el stock del insumo.
9. El sistema registra auditoría (fecha, hora, responsable y cantidad ingresada).
10. El sistema muestra mensaje de confirmación con el nuevo stock.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|----------|------------|----------|
| Entrada registrada correctamente | 201 | `{ "message": "Stock updated successfully", "new_stock": 120 }` |
| Insumo no encontrado | 404 | `{ "message": "Item not found" }` |
| Cantidad inválida | 422 | Detalle de errores de validación |
| No autorizado | 403 | `{ "message": "Forbidden" }` |

---

## Endpoint asociado

| Método | Ruta | Auth requerida |
|--------|------|---------------|
| POST | `/api/v1/inventory/items/{item_id}/entry` | Sí |

---

## Reglas de negocio

- **RN-024:** Solo usuarios autorizados pueden registrar entradas de inventario.
- **RN-025:** La cantidad ingresada debe ser mayor a cero.
- **RN-026:** Cada entrada debe registrarse como movimiento de inventario.
- **RN-027:** El stock debe actualizarse inmediatamente después del registro.
- **RN-028:** Toda entrada debe quedar registrada en auditoría con responsable, fecha y hora.
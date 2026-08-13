# RF-009 — Entrada de cantidades de insumo al inventario

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-009 |
| **Nombre** | Entrada de cantidades de insumo al inventario |
| **Módulo** | Inventario |
| **Prioridad** | Alta |
| **Estado** | Pendiente |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe permitir registrar entradas de insumos al inventario, incrementando automáticamente el stock disponible del insumo seleccionado. Cada entrada debe quedar registrada como movimiento para control histórico y auditoría.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `supply_id` | Entero | Sí | Debe existir en `supplies` |
| `quantity` | Decimal | Sí | Debe ser mayor a 0 |
| `provider_id` | Entero | No | Opcional |
| `notes` | Texto | No | Máximo 255 caracteres |

---

## Proceso

1. El usuario autorizado ingresa al módulo de inventario.
2. Selecciona la opción "Registrar entrada".
3. Selecciona el insumo y la cantidad recibida.
4. El sistema valida que el insumo exista y la cantidad sea mayor a cero.
5. Incrementa `available_quantity` del insumo.
6. Registra movimiento de entrada en el historial.
7. Registra auditoría (fecha, hora, responsable).

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Entrada registrada | 201 | Nuevo stock actualizado |
| Insumo no encontrado | 404 | Recurso no encontrado |
| Cantidad inválida | 422 | Detalle de errores |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| POST | `/inventory/supplies/{id}/entry` | Sí | Registrar entrada de insumo |

---

## Reglas de negocio

- **RN-059**: La cantidad ingresada debe ser mayor a cero.
- **RN-060**: Cada entrada debe registrarse como movimiento de inventario.
- **RN-061**: El stock debe actualizarse inmediatamente después del registro.
- **RN-062**: Toda entrada debe quedar registrada en auditoría.

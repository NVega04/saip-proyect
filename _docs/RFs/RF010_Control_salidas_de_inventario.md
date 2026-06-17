# RF-010 — Control de salidas de inventario

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-010 |
| **Nombre** | Control de salidas de inventario |
| **Módulo** | Inventario |
| **Prioridad** | Alta |
| **Estado** | Pendiente |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe permitir registrar, validar y controlar todas las salidas de insumos del inventario, asegurando que cada movimiento quede documentado con fecha, responsable y motivo de la salida. Debe impedir salidas que superen el stock disponible.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `supply_id` | Entero | Sí | Debe existir en `supplies` |
| `quantity` | Decimal | Sí | Mayor a 0 y menor o igual al stock disponible |
| `reason` | Texto | Sí | Motivo de la salida (producción, merma, ajuste, etc.) |

---

## Proceso

1. El usuario selecciona un insumo del inventario.
2. Ingresa la cantidad a retirar y el motivo.
3. El sistema valida que exista stock suficiente.
4. Si el stock es insuficiente, bloquea la operación.
5. Si es válido, descuenta la cantidad del `available_quantity`.
6. Registra movimiento de salida en el historial.
7. Si el stock queda por debajo del mínimo, muestra alerta.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Salida registrada | 201 | Nuevo stock actualizado |
| Stock insuficiente | 400 | Mensaje indicando stock disponible insuficiente |
| Datos inválidos | 422 | Detalle de errores |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| POST | `/inventory/supplies/{id}/output` | Sí | Registrar salida de insumo |

---

## Reglas de negocio

- **RN-063**: No se puede registrar una salida mayor al stock disponible.
- **RN-064**: Toda salida debe quedar asociada a un usuario responsable.
- **RN-065**: El inventario se actualiza inmediatamente después del registro.
- **RN-066**: Si el stock resultante es menor al mínimo, se muestra alerta.

# RF-016 — Control de stock de productos terminados

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-016 |
| **Nombre** | Control de stock de productos terminados |
| **Módulo** | Inventario / Ventas |
| **Prioridad** | Alta |
| **Estado** | Pendiente |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe controlar el stock de productos terminados, actualizándolo automáticamente mediante entradas por producción confirmada y salidas por ventas registradas. Debe impedir ventas con stock insuficiente y generar alertas cuando el stock esté por debajo del mínimo configurado.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `product_id` | Entero | Sí | Debe existir como producto terminado |
| `movement_type` | Enum | Sí | `PRODUCTION`, `SALE`, `ADJUSTMENT` |
| `quantity` | Decimal | Sí | Mayor a 0 |
| `reason` | Texto | Condicional | Obligatorio si `movement_type = ADJUSTMENT` |

---

## Proceso

### Por producción
1. Se confirma una orden de producción asociada a un producto terminado.
2. El sistema incrementa el `available_quantity` del producto.

### Por venta
1. Se registra una venta de producto terminado.
2. El sistema valida stock suficiente.
3. Si es válido, descuenta la cantidad vendida.

### Por ajuste manual
1. Usuario autorizado ingresa producto, cantidad y motivo.
2. El sistema registra el movimiento y actualiza el stock.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Movimiento registrado | 201 | Stock actualizado |
| Stock insuficiente | 400 | Mensaje de error |
| Usuario sin permisos | 403 | Acceso denegado |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| POST | `/inventory/products/movements` | Sí | Registrar movimiento de producto terminado |
| GET | `/inventory/products/stock` | Sí | Consultar stock actual |

---

## Reglas de negocio

- **RN-077**: Solo usuarios autorizados pueden realizar ajustes manuales.
- **RN-078**: El stock debe actualizarse inmediatamente tras la confirmación de cualquier movimiento.
- **RN-079**: No se permite registrar ventas que superen el stock disponible.
- **RN-080**: Todo movimiento debe registrar auditoría (usuario, tipo, fecha, motivo).
- **RN-081**: El sistema debe generar alertas cuando el stock sea menor al mínimo configurado.

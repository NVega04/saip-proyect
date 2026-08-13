# RF-019 — Registro de ventas de productos

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-019 |
| **Nombre** | Registro de ventas de productos |
| **Módulo** | Ventas |
| **Prioridad** | Alta |
| **Estado** | Pendiente |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe permitir registrar las ventas de productos (terminados y comerciales) de forma detallada, con selección de productos, cálculo de totales, validación de stock y descuento automático del inventario.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `items` | Lista | Sí | Arreglo de `{ product_id, quantity, unit_price }` |
| `payment_method` | Texto | Sí | Método de pago |

---

## Proceso

1. El usuario accede al módulo de ventas y selecciona "Nueva venta".
2. Agrega productos al carrito con cantidades.
3. El sistema valida stock disponible para cada producto.
4. Calcula subtotales, descuentos, impuestos y total.
5. Al confirmar, registra la venta y descuenta del inventario.
6. Si el stock resultante es menor al mínimo, muestra alerta.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Venta registrada | 201 | Datos de la venta y stock actualizado |
| Stock insuficiente | 400 | Detalle de productos sin stock |
| Datos inválidos | 422 | Errores de validación |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| POST | `/sales/` | Sí | Registrar venta |
| GET | `/sales/` | Sí | Historial de ventas |
| GET | `/sales/{id}` | Sí | Detalle de venta |

---

## Reglas de negocio

- **RN-082**: No se permiten ventas con cantidades superiores al stock disponible.
- **RN-083**: Cada venta descuenta automáticamente del inventario correspondiente.
- **RN-084**: Las ventas deben quedar registradas en el historial con usuario, fecha y hora.
- **RN-085**: Si el stock resultante es menor al mínimo, se muestra alerta visual.
- **RN-086**: Se debe poder consultar el historial de ventas con filtros por fecha y producto.

# RF-012 — Descontar materias primas al producir

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-012 |
| **Nombre** | Descontar materias primas al producir |
| **Módulo** | Producción / Inventario |
| **Prioridad** | Alta |
| **Estado** | Pendiente |
| **Fecha** | Febrero 2026 |

---

## Descripción

Al confirmar una orden de producción, el sistema debe descontar automáticamente del inventario las cantidades de materias primas definidas en la receta, calcular el rendimiento total y capturar snapshots del stock antes y después del consumo.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `production_order_id` | Entero | Sí | Debe existir y estar confirmada |
| `recipe_id` | Entero | Sí | Debe existir y estar activa |
| `quantity_multiplier` | Decimal | Sí | Mayor a 0 |

---

## Proceso

1. El sistema recibe la orden de producción confirmada.
2. Consulta la receta y sus cantidades requeridas por ingrediente.
3. Multiplica cada cantidad por el `quantity_multiplier`.
4. Valida disponibilidad de stock para cada insumo.
5. Si algún insumo falta, la operación completa se cancela.
6. Si todo es correcto, descuenta cada insumo y crea `ProductionOrderSnapshot` por cada uno (`stock_before`, `stock_after`, `quantity_used`).
7. Incrementa el stock del producto terminado asociado (si existe).
8. Registra auditoría completa.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Operación exitosa | 200 | Confirmación de descuentos |
| Stock insuficiente | 400 | Detalle de insumos faltantes |
| Datos inválidos | 422 | Errores de validación |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| POST | `/production/orders/{id}/complete` | Sí | Completar orden y descontar insumos |

---

## Reglas de negocio

- **RN-067**: Solo se ejecuta con orden previamente confirmada.
- **RN-068**: La receta debe estar vigente.
- **RN-069**: Debe validarse stock suficiente por cada insumo.
- **RN-070**: La operación es atómica; si falla un descuento no se realiza ninguno.
- **RN-071**: Se captura snapshot de stock antes/después por cada insumo.
- **RN-072**: Toda transacción debe generar auditoría completa.

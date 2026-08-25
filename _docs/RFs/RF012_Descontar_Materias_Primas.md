# RF-012 — Descontar materias primas al producir

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-012 |
| **Nombre** | Descontar materias primas al producir |
| **Módulo** | Producción / Inventario |
| **Prioridad** | Alta |
| **Estado** | Realizado |
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

---

## Implementación

**Backend** — `POST /production/orders/{id}/complete` en `backend/src/routers/production.py`:

1. Valida que la orden exista, no esté eliminada y esté en estado `in_progress` (404/409).
2. Valida receta vigente y activa, multiplicador mayor a 0 e ingredientes definidos (404/400).
3. Bloquea la operación si la unidad de algún ingrediente difiere de la unidad del insumo en inventario (400 con detalle), ya que no existe tabla de conversión de unidades.
4. Calcula `requerido = cantidad de receta × quantity_multiplier` por ingrediente.
5. Valida el stock de TODOS los insumos antes de mutar cualquiera: si falta alguno responde 400 con el detalle completo (`"Stock insuficiente... Faltantes: HARINA (requiere 2.0 KG, disponible 0.5 KG)"`) sin descontar nada.
6. Descuenta cada insumo y crea un `ProductionOrderSnapshot` por ingrediente (`stock_before`, `stock_after`, `quantity_used`).
7. Incrementa `available_quantity` del producto terminado asociado a la receta (`+= total_yield`) si existe.
8. Cambia el estado a `completed`, registra `completed_at` y auditoría (`updated_by`).
9. Ejecuta un único `session.commit()` al final del proceso.

**Concurrencia (RN-069/RN-070)**: para evitar condiciones de carrera entre confirmaciones simultáneas que comparten insumos, el endpoint adquiere **bloqueos pesimistas de fila** (`SELECT ... FOR UPDATE`) sobre todos los `Supply` involucrados dentro de la misma transacción, recorriéndolos en **orden determinista por id** para prevenir deadlocks. De esta forma, la lectura del stock y el descuento quedan serializados por fila: una segunda orden concurrente espera el bloqueo y ve el stock ya descontado. Si la validación falla, se lanza el error antes del commit y ningún dato es modificado.

**Frontend** — `frontend/src/pages/production/Production.tsx`: acción "Confirmar producción" disponible solo para órdenes `in_progress`, con diálogo previo (receta, multiplicador, rendimiento esperado y advertencia del descuento), notificación detallada de faltantes vía toast en caso de error 400, y actualización de la fila al completar.

**Robustez de la respuesta (bugfix)**: la respuesta se construye con datos planos (Pydantic) capturados bajo lock antes del commit — `ProductionSnapshotResponse` explícitos con `SupplyBasic`/`UnitBasic` — en lugar de pasar objetos ORM de SQLModel, que pydantic 2.12 rechaza en campos anidados y provocaba un 500 después del commit (el descuento sí se aplicaba, pero el frontend mostraba "error de servidor"). Adicionalmente, el frontend deshabilita las acciones de una fila mientras su petición está en vuelo (evita dobles confirmaciones → 409), re-obtiene la lista de órdenes desde el servidor tras cada operación (fuente de verdad) y normaliza `detail` cuando llega como lista de validación (422).

**Vínculo receta ↔ producto terminado**: el formulario de recetas incluye ahora el selector "Producto terminado" (`product_id`, opcional) que el backend ya soportaba; al completar una orden, el rendimiento se suma al stock de ese producto y aparece en Productos terminados. Si la receta no tiene producto asociado, el diálogo de confirmación lo advierte explícitamente y el stock de productos no se modifica.

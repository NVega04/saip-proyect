RF-012 — Descontar Materias Primas
<!-- ¿Qué? Requisito funcional que ejecuta el descuento automático de insumos al confirmar una orden de producción. ¿Para qué? Mantener la integridad del inventario y reflejar la fabricación del producto terminado. ¿Impacto? Sin este proceso el stock sería inconsistente y no habría trazabilidad confiable. -->

Identificación

| Campo         | Valor                       |
| ------------- | --------------------------- |
| **ID**        | RF-010                      |
| **Nombre**    | Descontar Materias Primas   |
| **Módulo**    | **Producción / Inventario** |
| **Prioridad** | Alta                        |
| **Estado**    | **Pendiente**               |
| **Fecha**     | **Septiembre 2025**         |

Descripción

Al confirmar una Orden de Producción, el sistema debe descontar automáticamente del inventario las cantidades de materias primas definidas en la lista de la receta y aumentar el stock del producto terminado.

Entradas

| Campo                 | Tipo   | Obligatorio | Validaciones                    |
| --------------------- | ------ | ----------- | ------------------------------- |
| `production_order_id` | **ID** | Sí          | Debe existir y estar confirmada |
| `recipe_version`      | **ID** | Sí          | Debe estar vigente              |
| `waste_percentage`    | Número | No          | Debe ser mayor o igual a 0      |
| `user_id`             | **ID** | Sí          | Usuario autenticado             |

Proceso

El sistema recibe la orden de producción confirmada.

Consulta la receta y sus cantidades requeridas.

Valida disponibilidad de stock por cada insumo (incluye conversiones y mínimos).

Aplica merma si fue configurada.

Si algún insumo falla, la operación completa se cancela.

Si todo es correcto, descuenta materias primas.

Incrementa el inventario del producto terminado.

Registra auditoría: quién, cuándo, sede, versión de receta y cantidades.

Vincula los movimientos con la orden de producción.

Salidas

| Escenario          | Código HTTP | Respuesta                                                     |
| ------------------ | ----------- | ------------------------------------------------------------- |
| Operación exitosa  | 200         | Confirmación de descuentos e incremento de producto terminado |
| Stock insuficiente | 400         | Detalle de insumos faltantes y cantidades requeridas          |
| Datos inválidos    | 422         | Errores de validación                                         |

Endpoint asociado

| Método | Ruta                                     | Auth requerida |
| ------ | ---------------------------------------- | -------------- |
| POST   | **/api/v1/production/consume-materials** | Sí             |

Reglas de negocio

RN-001: Solo se ejecuta con orden previamente confirmada.

RN-002: La receta debe estar vigente.

RN-003: Debe validarse stock suficiente por cada insumo.

RN-004: Puede configurarse merma por ítem o por orden.

RN-005: La operación es atómica; si falla un descuento no se realiza ninguno.

RN-006: Toda transacción debe generar auditoría completa.

RN-007: Si la orden se anula, los movimientos deben revertirse automáticamente.
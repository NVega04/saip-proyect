RF-010 — Control de salidas de inventario
<!-- ¿Qué? Requisito funcional que define el registro y control de las salidas de inventario. ¿Para qué? Garantizar trazabilidad y actualización automática del stock. ¿Impacto? Sin este requisito no habría control confiable de disminución de existencias. -->

Identificación

| Campo        | Tipo   | Obligatorio | Validaciones                                             |
| ------------ | ------ | ----------- | -------------------------------------------------------- |
| `product_id` | **ID** | Sí          | Debe existir en el inventario                            |
| `quantity`   | Número | Sí          | Debe ser mayor a 0 y no superar el stock disponible      |
| `reason`     | Texto  | Sí          | Valores permitidos: venta, producción, devolución, merma |
| `user_id`    | **ID** | Sí          | Debe corresponder a un usuario registrado                |
| `date`       | Fecha  | Sí          | No puede ser futura                                      |

Descripción

El sistema debe permitir registrar, validar y controlar todas las salidas de insumos y productos terminados del inventario, asegurando que cada movimiento quede documentado con fecha, responsable y motivo de la salida.

Entradas

| Campo        | Tipo   | Obligatorio | Validaciones                                             |
| ------------ | ------ | ----------- | -------------------------------------------------------- |
| `product_id` | **ID** | Sí          | Debe existir en el inventario                            |
| `quantity`   | Número | Sí          | Debe ser mayor a 0 y no superar el stock disponible      |
| `reason`     | Texto  | Sí          | Valores permitidos: venta, producción, devolución, merma |
| `user_id`    | **ID** | Sí          | Debe corresponder a un usuario registrado                |
| `date`       | Fecha  | Sí          | No puede ser futura                                      |

Proceso

El usuario selecciona el insumo o producto.

El usuario ingresa la cantidad a retirar y el motivo.

El sistema valida que exista stock suficiente.

El sistema registra la salida con fecha y responsable.

El inventario se actualiza automáticamente descontando la cantidad.

El movimiento queda almacenado en el historial para trazabilidad.

El sistema muestra un mensaje de confirmación del registro.
 
Salidas

| Escenario          | Código HTTP | Respuesta                                                 |
| ------------------ | ----------- | --------------------------------------------------------- |
| Registro exitoso   | 201         | Mensaje de confirmación y datos del movimiento            |
| Stock insuficiente | 400         | Mensaje de error indicando que no hay cantidad disponible |
| Datos inválidos    | 422         | Detalle de los errores de validación                      |

Endpoint asociado

| Método | Ruta                          | Auth requerida |
| ------ | ----------------------------- | -------------- |
| POST   | **/api/v1/inventory/outputs** | Sí             |

Reglas de negocio

RN-001: No se puede registrar una salida mayor al stock disponible.

RN-002: Toda salida debe quedar asociada a un usuario responsable.

RN-003: El inventario se actualiza inmediatamente después del registro.

RN-004: El historial de salidas debe poder consultarse mediante filtros por fecha, producto, usuario y motivo.

RN-005: El sistema debe confirmar visualmente cada salida registrada.
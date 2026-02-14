RF-014 — Registrar recetas de productos
<!-- ¿Qué? Requisito funcional para registrar la ejecución de una receta y la producción obtenida. ¿Para qué? Mantener trazabilidad y control automático del consumo de materias primas. ¿Impacto? Sin este requisito no habría coherencia entre producción e inventario. -->

Identificación

| Campo         | Valor                          |
| ------------- | ------------------------------ |
| **ID**        | RF-012                         |
| **Nombre**    | Registrar recetas de productos |
| **Módulo**    | **Producción / Recetas**       |
| **Prioridad** | Alta                           |
| **Estado**    | **Pendiente**                  |
| **Fecha**     | **Septiembre 2025**            |

Descripción

El sistema debe permitir registrar la producción basada en recetas, indicando las cantidades de producto terminado y los insumos utilizados, con el fin de mantener control sobre la trazabilidad y el consumo de materias primas.

Entradas

| Campo               | Tipo   | Obligatorio | Validaciones                |
| ------------------- | ------ | ----------- | --------------------------- |
| `recipe_id`         | **ID** | Sí          | Debe existir y estar activa |
| `produced_quantity` | Número | Sí          | Debe ser mayor a 0          |
| `production_date`   | Fecha  | Sí          | No puede ser futura         |
| `user_id`           | **ID** | Sí          | Usuario autenticado         |

Proceso

El usuario selecciona una receta previamente registrada.

Indica la cantidad de productos elaborados.

El sistema consulta la fórmula asociada (insumos y cantidades).

Se valida que exista stock suficiente.

Si la validación falla, se cancela la operación.

Si es correcta, el sistema descuenta automáticamente los insumos.

Se registra el historial de producción con fecha y responsable.

La información queda disponible para reportes.

Salidas

| Escenario          | Código HTTP | Respuesta                               |
| ------------------ | ----------- | --------------------------------------- |
| Registro exitoso   | 201         | Confirmación del registro de producción |
| Stock insuficiente | 400         | Mensaje indicando insumos faltantes     |
| Datos inválidos    | 422         | Detalle de errores                      |

Endpoint asociado

| Método | Ruta                        | Auth requerida |
| ------ | --------------------------- | -------------- |
| POST   | **/api/v1/recipes/produce** | Sí             |

Reglas de negocio

RN-001: La receta debe existir y tener fórmula definida.

RN-002: No puede registrarse producción sin stock suficiente.

RN-003: El descuento de insumos se realiza automáticamente.

RN-004: Debe guardarse historial con fecha, cantidad y responsable.

RN-005: Se deben permitir reportes filtrados por fecha, receta o usuario.
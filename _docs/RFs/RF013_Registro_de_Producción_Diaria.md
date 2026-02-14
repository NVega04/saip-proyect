RF-013 — Registro de Producción Diaria
<!-- ¿Qué? Requisito funcional para registrar la producción diaria de productos terminados. ¿Para qué? Permitir trazabilidad y preparación de movimientos de inventario posteriores. ¿Impacto? Sin este registro no existiría base formal para ejecutar el consumo de materias primas. -->

Identificación

| Campo         | Valor                         |
| ------------- | ----------------------------- |
| **ID**        | RF-009                        |
| **Nombre**    | Registro de Producción Diaria |
| **Módulo**    | **Producción**                |
| **Prioridad** | Alta                          |
| **Estado**    | **Pendiente**                 |
| **Fecha**     | **Septiembre 2025**           |

Descripción

El sistema debe permitir a un usuario autorizado registrar, por fecha y sede, la cantidad producida de cada producto terminado. Al guardar, se genera una Orden de Producción con estado y trazabilidad (usuario, fecha/hora, observaciones).

Entradas

| Campo             | Tipo   | Obligatorio | Validaciones                            |
| ----------------- | ------ | ----------- | --------------------------------------- |
| `product_id`      | **ID** | Sí          | Debe existir y ser producto terminado   |
| `quantity`        | Número | Sí          | Debe ser mayor a 0                      |
| `production_date` | Fecha  | Sí          | No puede ser futura según configuración |
| `site_id`         | **ID** | Sí          | Debe corresponder a una sede válida     |
| `status`          | Texto  | Sí          | Programada o Confirmada                 |
| `user_id`         | **ID** | Sí          | Usuario autenticado con permisos        |

Proceso

El usuario autorizado accede al módulo de producción.

Selecciona producto, fecha, sede y cantidad.

El sistema valida permisos y datos.

Se crea una Orden de Producción.

Se asigna estado inicial según configuración.

Se registran trazas: usuario, fecha/hora y observaciones.

La orden queda disponible para que el RF010 ejecute los movimientos de inventario cuando se confirme.

Salidas

| Escenario        | Código HTTP | Respuesta                                  |
| ---------------- | ----------- | ------------------------------------------ |
| Registro exitoso | 201         | Datos de la orden creada con identificador |
| No autorizado    | 403         | Mensaje de acceso denegado                 |
| Datos inválidos  | 422         | Errores de validación                      |

Endpoint asociado

| Método | Ruta                          | Auth requerida |
| ------ | ----------------------------- | -------------- |
| POST   | **/api/v1/production/orders** | Sí             |

Reglas de negocio

RN-001: Solo usuarios con rol autorizado pueden registrar producción.

RN-002: El producto debe estar marcado como producto terminado.

RN-003: Debe indicarse fecha, sede y cantidad válida.

RN-004: La orden inicia en estado Programada o Confirmada según parámetros del sistema.

RN-005: Este proceso no modifica inventario directamente.

RN-006: La afectación de stock se realiza posteriormente mediante el RF010.

RN-007: Debe mantenerse trazabilidad completa de la operación.

RN-008: La operación debe completarse en menos de un minuto.
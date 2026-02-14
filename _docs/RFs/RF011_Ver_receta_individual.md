RF-011 — Ver receta individual
<!-- ¿Qué? Requisito funcional que permite consultar el detalle completo de una receta. ¿Para qué? Facilitar la planificación y el control de la producción. ¿Impacto? Sin esta funcionalidad no habría visibilidad detallada ni apoyo a la toma de decisiones. -->

Identificación

| Campo         | Valor                 |
| ------------- | --------------------- |
| **ID**        | RF-050                |
| **Nombre**    | Ver receta individual |
| **Módulo**    | **Recetas**           |
| **Prioridad** | Alta                  |
| **Estado**    | **Pendiente**         |
| **Fecha**     | **Septiembre 2025**   |

Descripción

El sistema debe permitir a los usuarios consultar de manera detallada la información completa de una receta específica, incluyendo nombre, categoría y lista de ingredientes, con el fin de apoyar la planificación y control en la producción de la panadería.

Entradas

| Campo       | Tipo   | Obligatorio | Validaciones                                         |
| ----------- | ------ | ----------- | ---------------------------------------------------- |
| `recipe_id` | **ID** | Sí          | Debe existir y estar activo en el sistema            |
| `user_id`   | **ID** | Sí          | Debe estar autenticado y tener permisos según su rol |

Proceso

El usuario accede al listado general de recetas.

Selecciona una receta específica.

El sistema valida autenticación y permisos.

El sistema consulta la información almacenada.

Se muestran nombre, categoría, ingredientes, cantidades, pasos, tiempos y costos.

La vista es solo de lectura.

El usuario puede regresar al listado general.

Salidas

| Escenario            | Código HTTP | Respuesta                                       |
| -------------------- | ----------- | ----------------------------------------------- |
| Consulta exitosa     | 200         | Datos completos de la receta                    |
| No autorizado        | 403         | Mensaje de acceso denegado                      |
| Receta no encontrada | 404         | Mensaje indicando que no existe o está inactiva |

Endpoint asociado

| Método | Ruta                            | Auth requerida |
| ------ | ------------------------------- | -------------- |
| GET    | **/api/v1/recipes/{recipe_id}** | Sí             |

Reglas de negocio

RN-001: Solo usuarios autenticados pueden visualizar recetas.

RN-002: Los permisos dependen del rol asignado.

RN-003: La información es únicamente de consulta; no se permite edición desde esta vista.

RN-004: No deben mostrarse recetas eliminadas o incompletas.

RN-005: La interfaz debe mantener consistencia visual y permitir volver al listado.
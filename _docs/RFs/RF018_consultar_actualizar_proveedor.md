# RF018: Consultar y Actualizar Proveedor

---

# 2. Identificación

## Identificación

| Campo             | Valor                                   |
| ----------------- | --------------------------------------- |
| **ID**            | RF-018                                  |
| **Nombre**        | Consultar y Actualizar Proveedor        |
| **Módulo**        | Compras / Catálogo de Proveedores       |
| **Prioridad**     | Media-Alta                              |
| **Estado**        | Pendiente de implementación             |
| **Fecha**         | Febrero 2026                            |

---

# 3. Descripción

El sistema debe permitir la visualización detallada de la información de los proveedores registrados, así como la actualización de sus datos de contacto y condiciones comerciales.

Esta funcionalidad garantiza que la administración de la panadería cuente siempre con información vigente para la gestión de compras, permitiendo modificar campos como:

- Teléfono  
- Dirección  
- Persona de contacto  
- Correos electrónicos  
- Condiciones comerciales  

Las modificaciones deben realizarse sin perder el historial del proveedor, preservando la trazabilidad de cambios.

El sistema no debe permitir la eliminación física de registros; únicamente se permitirá cambiar el estado del proveedor a **Inactivo** cuando ya no se utilice.

---

# 4. Entradas

## Entradas

| Campo               | Tipo          | Obligatorio | Validaciones                                                   |
| ------------------- | ------------- | ----------- | -------------------------------------------------------------- |
| `provider_id`       | UUID / Entero | Sí          | Debe existir en el catálogo                                    |
| `phone`             | Texto         | No          | Formato válido de teléfono                                     |
| `email`             | Texto (email) | No          | Formato de email válido, máximo 255 caracteres                 |
| `address`           | Texto         | No          | Máximo 255 caracteres                                          |
| `contact_person`    | Texto         | No          | Máximo 255 caracteres                                          |
| `commercial_terms`  | Texto         | No          | Máximo 500 caracteres                                          |
| `status`            | Enum          | No          | Valores permitidos: `ACTIVE`, `INACTIVE`                       |
| `updated_by`        | UUID / Entero | Sí          | Usuario autenticado con rol autorizado                         |

---

# 5. Proceso Paso a Paso del Requerimiento

## Consulta de Proveedor

1. El usuario accede al módulo de Proveedores.  
2. El sistema permite buscar proveedores por nombre, identificación o contacto.  
3. El usuario selecciona un proveedor del listado.  
4. El sistema muestra la información completa del proveedor de forma clara y estructurada.  
5. Se registra automáticamente un log de consulta con usuario, fecha y hora.

## Actualización de Proveedor

1. El usuario accede a la opción de edición.  
2. El sistema valida que el usuario tenga rol **Administrador** o **Compras**.  
3. El usuario modifica los campos permitidos.  
4. El sistema valida:
   - Formato correcto de correo electrónico (si se modifica).  
   - Formato válido de teléfono (si se modifica).  
5. El usuario confirma los cambios.  
6. El sistema:
   - Guarda la actualización en base de datos.  
   - Mantiene el historial de cambios.  
   - Registra automáticamente un log de auditoría con usuario, fecha y hora.  

---

# 6. Salidas

## Salidas

| Escenario                                  | Código HTTP | Respuesta                                                      |
| ------------------------------------------ | ----------- | -------------------------------------------------------------- |
| Consulta exitosa                           | 200         | Datos completos del proveedor                                 |
| Actualización exitosa                      | 200         | Datos actualizados del proveedor                              |
| Usuario sin permisos                       | 403         | Mensaje de error: "Unauthorized action"                       |
| Proveedor no encontrado                    | 404         | Mensaje de error: "Provider not found"                        |
| Error de validación                        | 422         | Detalle de errores de validación                              |

---

## Endpoint Asociado

| Método | Ruta                          | Auth requerida |
| ------ | ----------------------------- | -------------- |
| GET    | `/api/v1/providers/{id}`      | Sí             |
| GET    | `/api/v1/providers`           | Sí             |
| PUT    | `/api/v1/providers/{id}`      | Sí             |
| PATCH  | `/api/v1/providers/{id}`      | Sí             |

---

# 7. Reglas de Negocio

1. **Permisos de Acceso**  
   - Solo usuarios con rol **Administrador** o **Compras** pueden editar proveedores.  
   - Otros roles solo pueden consultar si tienen permisos de lectura.

2. **Validación de Datos**  
   - El correo electrónico y teléfono deben pasar por el mismo proceso de validación aplicado en la creación (RF017).  

3. **Historial de Cambios**  
   - No se permite eliminación física del proveedor.  
   - Solo se permite cambiar su estado a `INACTIVE`.  
   - Toda modificación debe quedar registrada en auditoría.

4. **Registro de Auditoría**  
   Cada consulta o edición debe registrar automáticamente:
   - Usuario  
   - Fecha  
   - Hora  
   - Tipo de acción (`VIEW` o `UPDATE`)

5. **Consulta Eficiente**  
   El sistema debe permitir búsqueda rápida y filtrable desde el catálogo para facilitar la gestión operativa.

---

# Impacto en el Sistema

Este requerimiento permite:

- Mantener información actualizada para la gestión de compras.  
- Garantizar trazabilidad y control administrativo.  
- Evitar pérdida de datos históricos.  
- Mejorar la eficiencia operativa mediante consultas rápidas y seguras.

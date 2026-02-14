# RF017: Crear proveedor

---

## Identificación

| Campo             | Valor                          |
| ----------------- | ------------------------------ |
| **ID**            | RF-017                         |
| **Nombre**        | Crear Proveedor                |
| **Módulo**        | Compras / Catálogo de Proveedores |
| **Prioridad**     | Media-Alta                     |
| **Estado**        | Pendiente de implementación    |
| **Fecha**         | Febrero 2026                   |

---

# Descripción

El sistema debe permitir registrar nuevos proveedores en el catálogo institucional, almacenando información básica necesaria para la gestión de compras y abastecimiento.

La información a registrar incluye:

- Nombre o razón social  
- Identificación (NIT / RUC / RFC u otro identificador fiscal)  
- Dirección  
- Teléfono  
- Correo electrónico  
- Persona de contacto  
- Forma de pago  

Una vez creado, el proveedor debe quedar disponible inmediatamente para consulta y selección en los procesos del módulo de compras.

El sistema no permitirá la eliminación física de proveedores. En su lugar, solo se permitirá la baja lógica (soft delete), conservando la integridad histórica de la información.

---

## Entradas

| Campo               | Tipo          | Obligatorio | Validaciones                                              |
| ------------------- | ------------- | ----------- | --------------------------------------------------------- |
| `name`              | Texto         | Sí          | Mínimo 2 caracteres, máximo 255                          |
| `identification`    | Texto         | Sí          | No vacío, debe ser único en el sistema                   |
| `address`           | Texto         | No          | Máximo 255 caracteres                                    |
| `phone`             | Texto         | Sí          | Formato válido de teléfono                               |
| `email`             | Texto (email) | Sí          | Formato de email válido, máximo 255, único en el sistema |
| `contact_person`    | Texto         | No          | Máximo 255 caracteres                                    |
| `payment_method`    | Texto / Enum  | No          | Debe corresponder a formas de pago configuradas          |
| `created_by`        | UUID / Entero | Sí          | Usuario autenticado con rol autorizado                   |

---

# 5. Proceso Paso a Paso del Requerimiento

1. El usuario accede al módulo de Proveedores.  
2. Selecciona la opción "Crear nuevo proveedor".  
3. El sistema valida que el usuario tenga rol **Administrador**.  
4. El usuario completa los campos obligatorios y opcionales.  
5. El sistema valida:
   - Campos obligatorios completos.  
   - Formato correcto de correo electrónico.  
   - Formato válido de teléfono.  
   - Unicidad de identificación y correo electrónico.  
6. El usuario confirma el registro.  
7. El sistema:
   - Guarda el proveedor en la base de datos.  
   - Lo marca como activo por defecto.  
   - Registra automáticamente un log de auditoría con usuario y fecha de creación.  
8. El proveedor aparece inmediatamente en el catálogo disponible para consulta.

---

# 6. Salidas

## Salidas

| Escenario                               | Código HTTP | Respuesta                                                  |
| ---------------------------------------- | ----------- | ---------------------------------------------------------- |
| Proveedor creado exitosamente            | 201         | Datos del proveedor creado (`id`, `name`, `email`, `status`, `created_at`) |
| Usuario sin permisos                     | 403         | Mensaje de error: "Unauthorized action"                    |
| Identificación o email ya registrado     | 400         | Mensaje de error: "Provider already exists"                |
| Datos inválidos                          | 422         | Detalle de errores de validación                           |

---

## Endpoint Asociado

| Método | Ruta                         | Auth requerida |
| ------ | ---------------------------- | -------------- |
| POST   | `/api/v1/providers`          | Sí             |
| GET    | `/api/v1/providers`          | Sí             |
| PATCH  | `/api/v1/providers/{id}`     | Sí             |

---

# 7. Reglas de Negocio

1. **Control de Acceso**  
   Solo usuarios con rol **Administrador** pueden crear proveedores.

2. **Campos Obligatorios**  
   Son obligatorios:  
   - Nombre  
   - Identificación  
   - Correo electrónico  
   - Teléfono  

3. **Validaciones de Formato**  
   - El correo electrónico debe cumplir formato estándar válido.  
   - El teléfono debe cumplir un formato numérico válido según configuración del sistema.

4. **Unicidad de Datos**  
   - La identificación debe ser única.  
   - El correo electrónico debe ser único.

5. **No Eliminación Física**  
   No se permite eliminar proveedores de forma permanente.  
   Solo se permite baja lógica (soft delete), conservando la trazabilidad histórica.

6. **Auditoría Obligatoria**  
   Cada creación debe generar un registro automático que incluya:
   - Usuario creador  
   - Fecha y hora  
   - Tipo de operación (CREATE)

---

# Impacto en el sistema

Este requerimiento garantiza:

- Control estructurado del catálogo de proveedores.  
- Integridad histórica de la información.  
- Seguridad mediante control de roles.  
- Base confiable para órdenes de compra, cuentas por pagar y trazabilidad financiera.

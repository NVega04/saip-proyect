# RF-001 — Gestión de usuario
<!--
  ¿Qué? Requisito funcional que define la gestión completa (CRUD) de usuarios por parte del administrador en el sistema SAIP.
  ¿Para qué? Permitir al administrador crear, actualizar, desactivar y eliminar cuentas de empleados de forma segura y controlada.
  ¿Impacto? Sin este requisito, no se podría incorporar o gestionar personal (cajeros, panaderos, repartidores, etc.) de manera segura en el sistema.
-->
---

## Identificación

| Campo         | Valor                          |
|---------------|--------------------------------|
| **ID**        | RF-001                         |
| **Nombre**    | Gestión de usuario             |
| **Módulo**    | Autenticación y Administración |
| **Prioridad** | Alta                           |
| **Estado**    | implementado                   |
| **Fecha**     | Febrero 2026                   |

---

## Descripción

El sistema debe permitir **exclusivamente al usuario con rol Administrador** crear, actualizar, desactivar/activar y eliminar (lógicamente) los usuarios del sistema (empleados: cajeros, panaderos, repartidores, contador, etc.).

La gestión se realiza desde un panel administrativo seguro, con control de acceso basado en roles (RBAC). No existe registro público ni formulario de auto-registro.

---

## Entradas (Formulario de creación/edición – solo accesible por Admin)


| Campo              | Tipo          | Obligatorio | Validaciones                                                                                   |
|--------------------|---------------|-------------|------------------------------------------------------------------------------------------------|
| `full_name`        | Texto         | Sí          | Mínimo 2 caracteres, máximo 255 caracteres                                                     |
| `username`         | Texto         | Sí          | Único en el sistema, sin espacios, solo alfanuméricos + guiones bajos/medio                    |
| `email`            | Texto (email) | Sí          | Formato de email válido, máximo 255 caracteres, debe ser único en el sistema                   |
| `phone`            | Texto         | No          | Formato teléfono válido (opcional según negocio)                                               |
| `document_number`  | Texto         | No          | Número de identificación (cédula, etc.) – único si se usa (opcional)                           |
| `role`             | Selección     | Sí          | Dropdown con roles predefinidos (Administrador, Cajero, Panadero, Repartidor, Contador, etc.) |
| `password`         | Texto         | Sí (creación) | Mínimo 8 caracteres, al menos 1 mayúscula, 1 minúscula, 1 número (temporal o generada auto)   |
| `confirm_password` | Texto         | Sí (creación) | Debe coincidir exactamente con `password`                                                      |
| `is_active`        | Booleano      | Sí (edición) | Activo / Inactivo (para desactivar sin eliminar)                                               |

---

## Proceso (CRUD gestionado por Administrador)

1. El Administrador inicia sesión y accede al módulo "Gestión de Usuarios" (protegido por autenticación y autorización RBAC).
2. Para **crear**:
   - Accede a formulario "+ Nuevo Usuario".
   - Completa los campos (frontend valida formatos, coincidencia de contraseñas, etc.).
   - Envía POST al backend.
3. Backend (con autenticación):
   - Verifica que el solicitante tenga rol Administrador.
   - Valida datos con Pydantic o similar (formatos, unicidad de email/username, fortaleza contraseña).
   - Hashea la contraseña con bcrypt (o argon2 recomendado en 2026).
   - Crea registro en tabla `users` con estado `active=true`, `created_by` = ID del admin actual.
   - Genera contraseña temporal si no se ingresó manualmente.
   - Envía email automático al nuevo usuario con credenciales + instrucción de cambio en primer login.
4. Para **actualizar** / **desactivar** / **eliminar**:
   - Desde lista de usuarios → selecciona uno → acciones correspondientes.
   - Actualización: permite cambiar nombre, email, rol, teléfono, etc. (no contraseña aquí – ver cambio separado).
   - Desactivación: cambia `is_active=false` → impide login.
   - Eliminación: preferible lógica (`deleted_at` timestamp o `is_deleted=true`) para mantener auditoría.
5. Todas las operaciones registran auditoría (created_by, updated_by, deleted_by, timestamps).

---

## Salidas (Respuestas API y mensajes UI)

| Escenario                        | Código HTTP | Respuesta / Mensaje UI                                                                 |
|----------------------------------|-------------|----------------------------------------------------------------------------------------|
| Creación exitosa                 | 201         | Datos del usuario creado (id, username, email, full_name, role, created_at) – sin password |
| Email o username ya registrado   | 400         | "El correo electrónico ya está registrado" o "El nombre de usuario ya está en uso"     |
| Datos inválidos / validación fallida | 422     | Detalle de errores por campo (ej: "password: debe contener al menos una mayúscula")    |
| Acceso denegado (no es Admin)    | 403         | "Acceso no autorizado: solo administradores pueden gestionar usuarios"                 |
| Usuario desactivado correctamente| 200         | "Usuario desactivado exitosamente"                                                     |
| Eliminación lógica exitosa       | 200         | "Usuario eliminado (lógicamente)"                                                      |
| Error interno                    | 500         | Mensaje genérico: "Error al procesar la operación"                                     |

---

## Endpoints asociados (protegidos por autenticación)

| Método | Ruta                                | Auth requerida          | Descripción                          |
|--------|-------------------------------------|-------------------------|--------------------------------------|
| GET    | `/api/v1/users`                     | Sí (rol: Administrador) | Lista de usuarios (con filtros)      |
| POST   | `/api/v1/users`                     | Sí (rol: Administrador) | Crear nuevo usuario                  |
| GET    | `/api/v1/users/{user_id}`           | Sí (rol: Administrador) | Obtener detalles de un usuario       |
| PUT    | `/api/v1/users/{user_id}`           | Sí (rol: Administrador) | Actualizar usuario                   |
| PATCH  | `/api/v1/users/{user_id}/status`    | Sí (rol: Administrador) | Cambiar estado (activar/desactivar)  |
| DELETE | `/api/v1/users/{user_id}`           | Sí (rol: Administrador) | Eliminación lógica                   |
| POST   | `/api/v1/users/{user_id}/resend-credentials` | Sí (rol: Admin) | Reenviar credenciales por email |

---

## Reglas de negocio

- **RN-001**: Solo usuarios con rol **Administrador** pueden acceder a cualquier operación de gestión de usuarios (crear, leer lista completa, actualizar, desactivar, eliminar).
- **RN-002**: El correo electrónico y username deben ser únicos en todo el sistema.
- **RN-003**: La contraseña nunca se almacena en texto plano; siempre se hashea con bcrypt (o algoritmo más seguro como Argon2).
- **RN-004**: La contraseña inicial debe cumplir requisitos mínimos de fortaleza (mínimo 8 caracteres, 1 mayúscula, 1 minúscula, 1 número).
- **RN-005**: Al crear usuario, se envía notificación por correo con credenciales temporales + enlace al login y obligación de cambio en primer inicio de sesión.
- **RN-006**: Todas las operaciones de gestión deben registrar auditoría (quién hizo qué, cuándo).
- **RN-007**: El nuevo usuario debe cambiar la contraseña temporal en su primer inicio de sesión (controlado por flag `must_change_password`).

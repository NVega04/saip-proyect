# RF-001 — Gestión de usuario

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-001 |
| **Nombre** | Gestión de usuario |
| **Módulo** | Administración / Gestión de usuarios |
| **Prioridad** | Alta |
| **Estado** | Implementado |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe permitir **exclusivamente al usuario con rol Administrador** (`is_admin = true`) crear, actualizar, desactivar/activar y eliminar lógicamente los usuarios del sistema (empleados: cajeros, panaderos, repartidores, etc.).

La gestión se realiza desde un panel administrativo seguro, con control de acceso basado en roles (RBAC) y protección mediante token híbrido JWT + sesión en base de datos. No existe registro público ni formulario de auto-registro.

---

## Entradas (Formulario de creación/edición – solo accesible por Admin)

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `first_name` | Texto | Sí | Máximo 100 caracteres |
| `last_name` | Texto | Sí | Máximo 100 caracteres |
| `email` | Texto (email) | Sí | Formato de email válido, máximo 150 caracteres, único en el sistema |
| `phone` | Texto | No | Máximo 20 caracteres |
| `role_id` | Selección (entero) | Sí | Debe corresponder a un rol existente en la tabla `roles` |
| `is_admin` | Booleano | Sí | Define si el usuario tiene permisos de administrador |

---

## Proceso (CRUD gestionado por Administrador)

1. El Administrador inicia sesión mediante token híbrido JWT + sesión y accede al módulo "Usuarios" (protegido por `require_admin`).
2. Para **crear**:
   - Accede a formulario "+ Nuevo usuario".
   - Completa los campos (frontend valida formatos).
   - Envía `POST /users/` al backend con el JWT en header `session-token`.
3. Backend:
   - Verifica que el solicitante tenga `is_admin = true`.
   - Valida datos con Pydantic (formatos, unicidad de email).
   - Genera contraseña temporal (`Temp@XXXXYY`) y la hashea con bcrypt.
   - Crea registro en tabla `users` con `status = active`, `created_by` = ID del admin actual.
   - Envía email automático al nuevo usuario con credenciales.
4. Para **editar** / **desactivar** / **eliminar**:
   - Desde lista de usuarios → selecciona uno → acciones correspondientes.
   - Edición: `PUT /users/{id}` permite cambiar nombre, email, rol, teléfono, estado, `is_admin`.
   - Desactivación: cambia `status = inactive` → impide login ("El usuario está inactivo. Contacte al administrador.").
   - Eliminación: lógica (`deleted_at`, `deleted_by`) para mantener auditoría.
5. Todas las operaciones registran auditoría (`created_by`, `updated_by`, `deleted_by`, timestamps).

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Creación exitosa | 201 | Datos del usuario creado (sin password) |
| Email ya registrado | 400 | "El correo electrónico ya está registrado" |
| Datos inválidos | 422 | Detalle de errores por campo |
| Acceso denegado (no es Admin) | 403 | "Se requieren permisos de administrador." |
| Usuario desactivado correctamente | 200 | Mensaje de confirmación |
| Eliminación lógica exitosa | 200 | Mensaje de confirmación con `deleted_at` y `deleted_by` |
| No autenticado | 401 | "Token inválido" / "Sesión expirada" |
| Error interno | 500 | Mensaje genérico |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| GET | `/users/` | Admin | Lista de usuarios |
| GET | `/users/me` | Usuario autenticado | Perfil del usuario actual |
| POST | `/users/` | Admin | Crear nuevo usuario |
| PUT | `/users/{id}` | Admin | Actualizar usuario |
| DELETE | `/users/me` | Usuario autenticado | Baja de cuenta propia (requiere confirmación de contraseña) |
| DELETE | `/users/{id}` | Admin | Eliminación lógica de usuario |

---

## Reglas de negocio

- **RN-001**: Solo usuarios con `is_admin = true` pueden acceder a cualquier operación de gestión de usuarios.
- **RN-002**: El correo electrónico debe ser único en todo el sistema.
- **RN-003**: La contraseña nunca se almacena en texto plano; siempre se hashea con bcrypt.
- **RN-004**: Al crear usuario, se genera contraseña temporal (`Temp@XXXXYY`) y se envía por correo.
- **RN-005**: Todas las operaciones de gestión deben registrar auditoría (quién hizo qué, cuándo).
- **RN-006**: La eliminación es lógica (soft delete), no física.

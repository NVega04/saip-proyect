# RF-006 — Dar de baja a usuarios

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-006 |
| **Nombre** | Dar de baja a usuarios |
| **Módulo** | Administración / Gestión de usuarios |
| **Prioridad** | Alta |
| **Estado** | Implementado |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe permitir que un administrador pueda desactivar o eliminar lógicamente usuarios registrados. La desactivación cambia el estado a `inactive` impidiendo el inicio de sesión. La eliminación lógica (soft delete) preserva los datos para auditoría.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `user_id` | Entero | Sí | Debe existir en base de datos |
| `status` | Enum (edición) | No | `active` / `inactive` |

---

## Proceso

1. El administrador ingresa al módulo de usuarios (`/usuarios`).
2. El sistema muestra la lista de usuarios en una tabla.
3. El administrador selecciona un usuario y elige:
   - **Desactivar**: cambia `status = inactive`, el usuario no puede iniciar sesión.
   - **Activar**: cambia `status = active`, restaura el acceso.
   - **Eliminar**: establece `deleted_at` y `deleted_by` (soft delete).
4. En todos los casos se registra auditoría (responsable, fecha, hora).

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Usuario actualizado | 200 | Datos del usuario actualizado |
| Eliminación lógica exitosa | 200 | Mensaje de confirmación |
| Usuario no encontrado | 404 | Recurso no encontrado |
| No autorizado | 403 | "Se requieren permisos de administrador." |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| PUT | `/users/{id}` | Admin | Actualizar usuario (incluye cambio de estado) |
| DELETE | `/users/{id}` | Admin | Eliminación lógica de usuario |

---

## Reglas de negocio

- **RN-029**: Solo usuarios con `is_admin = true` pueden dar de baja usuarios.
- **RN-030**: No se permite eliminar físicamente usuarios; solo baja lógica o cambio de estado.
- **RN-031**: El usuario dado de baja (`inactive`) no podrá iniciar sesión ("El usuario está inactivo. Contacte al administrador.").
- **RN-032**: Toda operación debe registrarse en auditoría.

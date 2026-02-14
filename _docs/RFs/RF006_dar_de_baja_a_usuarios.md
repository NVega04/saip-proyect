# RF-006 — Dar de baja a usuarios

---

## Identificación

| Campo | Valor |
|------|-------|
| ID | RF-006 |
| Nombre | Dar de baja a usuarios |
| Módulo | Administración de Usuarios |
| Prioridad | Alta |
| Estado | Pendiente |
| Fecha | Febrero 2026 |

---

## Descripción

El sistema debe permitir que un administrador pueda dar de baja a usuarios registrados en el sistema, cambiando su estado a **Inactivo**.  
Esta acción debe impedir que el usuario vuelva a iniciar sesión, pero sin eliminar su información para fines de auditoría y trazabilidad.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|------|------|-------------|--------------|
| user_id | UUID / Int | Sí | Debe existir en base de datos |
| motivo | Texto | Sí | No vacío, mínimo 5 caracteres |

---

## Proceso

1. El administrador ingresa al módulo de gestión de usuarios.
2. El sistema muestra el listado de usuarios registrados.
3. El administrador selecciona un usuario activo.
4. El administrador selecciona la opción **Dar de baja**.
5. El sistema solicita el motivo de la baja.
6. El sistema valida que el usuario exista y que esté en estado activo.
7. El sistema actualiza el estado del usuario a **Inactivo**.
8. El sistema registra la operación en auditoría (responsable, fecha, hora y motivo).
9. El sistema muestra un mensaje de confirmación.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|----------|------------|----------|
| Usuario dado de baja exitosamente | 200 | `{ "message": "User deactivated successfully" }` |
| Usuario no encontrado | 404 | `{ "message": "User not found" }` |
| Usuario ya inactivo | 409 | `{ "message": "User is already inactive" }` |
| Datos inválidos | 422 | Detalle de errores de validación |
| No autorizado | 403 | `{ "message": "Forbidden" }` |

---

## Endpoint asociado

| Método | Ruta | Auth requerida |
|--------|------|---------------|
| PATCH | `/api/v1/users/{user_id}/deactivate` | Sí |

---

## Reglas de negocio

- **RN-010:** Solo los usuarios con rol **Administrador** pueden dar de baja usuarios.
- **RN-011:** No se permite dar de baja a un usuario que ya esté inactivo.
- **RN-012:** El usuario dado de baja no podrá iniciar sesión en el sistema.
- **RN-013:** La baja debe registrarse en auditoría con fecha, hora, responsable y motivo obligatorio.
- **RN-014:** El sistema no debe eliminar el usuario, solo cambiar su estado a **Inactivo**.
# HU-006 — Dar de baja usuario

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-006 |
| Título | Dar de baja usuario |
| Módulo | Administración / Gestión de usuarios |
| Prioridad | Alta |
| Estado | Completado |
| RF asociados | RF006 |

---

## Historia

Como administrador, quiero desactivar o eliminar usuarios del sistema, para controlar el acceso de empleados que ya no laboran en la panadería o que no deben acceder al sistema.

---

## Criterios de aceptación

### CA-006.1 — Desactivación de usuario (cambio de estado)

**Dado** que selecciono un usuario activo desde la lista de usuarios como Administrador,
**cuando** elijo la opción "Desactivar" y confirmo la acción,
**entonces** el sistema cambia el estado del usuario a `inactive`, el usuario ya no puede iniciar sesión (el sistema muestra "El usuario está inactivo. Contacte al administrador."), se registra auditoría (`updated_at`, `updated_by`) y la lista se actualiza.

### CA-006.2 — Reactivación de usuario

**Dado** que selecciono un usuario inactivo desde la lista de usuarios como Administrador,
**cuando** elijo la opción "Activar",
**entonces** el sistema cambia el estado del usuario a `active`, puede volver a iniciar sesión con sus credenciales anteriores, y se registra auditoría.

### CA-006.3 — Eliminación lógica de usuario (soft delete)

**Dado** que selecciono un usuario de la lista como Administrador,
**cuando** elijo la opción "Eliminar" y confirmo (con advertencia de que la operación es irreversible),
**entonces** el sistema realiza una eliminación lógica:
- Establece `deleted_at` con la fecha/hora actual
- Establece `deleted_by` con el ID del administrador que realiza la operación
- El usuario desaparece de la lista principal
- Se mantiene trazabilidad completa en base de datos
- Se registra auditoría

### CA-006.4 — Protección contra auto-eliminación

**Dado** que soy Administrador,
**cuando** intento eliminarme a mí mismo de la lista de usuarios,
**entonces** el sistema debe permitir la operación (el usuario puede darse de baja a sí mismo mediante el modal de "Eliminar cuenta" que requiere confirmación de contraseña).

### CA-006.5 — Baja de cuenta propia desde el perfil

**Dado** que estoy autenticado y accedo a mi perfil,
**cuando** selecciono la opción "Eliminar mi cuenta" y confirmo con mi contraseña actual,
**entonces** el sistema:
- Recibe la contraseña en el header `X-Confirm-Password`
- Verifica que la contraseña coincida con el hash almacenado
- Realiza eliminación lógica (soft delete)
- Limpia la sesión y redirige al login

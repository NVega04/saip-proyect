# HU-005 — Cerrar sesión

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-005 |
| Título | Cerrar sesión |
| Módulo | Autenticación |
| Prioridad | Alta |
| Estado | Completado |
| RF asociados | RF005 |

---

## Historia

Como usuario autenticado, quiero cerrar sesión (individual o en todos los dispositivos), para proteger mi información y controlar el acceso a mi cuenta.

---

## Criterios de aceptación

### CA-005.1 — Cierre de sesión individual

**Dado** que estoy autenticado y tengo una sesión activa,
**cuando** selecciono la opción "Cerrar sesión",
**entonces** el sistema:
- Envía el JWT actual al backend (`POST /session/logout`)
- El backend decodifica el JWT, extrae el UUID interno de sesión
- Marca la sesión en base de datos como `is_active = false`
- El frontend limpia `localStorage` (token, módulos, datos de usuario)
- Redirige a la pantalla de login

### CA-005.2 — Cierre de sesión en todos los dispositivos

**Dado** que estoy autenticado y tengo sesiones activas en múltiples dispositivos,
**cuando** selecciono la opción "Cerrar sesión en todos los dispositivos",
**entonces** el sistema:
- Envía la solicitud al backend (`POST /session/logout-all`)
- El backend busca todas las sesiones activas del usuario
- Marca todas como `is_active = false`
- El frontend limpia `localStorage` y redirige al login
- Cualquier otro dispositivo con una sesión previa quedará invalidado en su próximo request

### CA-005.3 — Token inválido al cerrar sesión

**Dado** que mi token ya fue invalidado (por cierre previo, cambio de contraseña o expiración),
**cuando** intento cerrar sesión,
**entonces** el backend responde con error 401 o 404, y el frontend limpia `localStorage` y redirige al login igualmente.

### CA-005.4 — Persistencia del cierre de sesión

**Dado** que he cerrado sesión correctamente,
**cuando** intento realizar cualquier operación que requiera autenticación,
**entonces** el backend rechaza la solicitud con error 401 porque la sesión está marcada como inactiva en BD, y el frontend redirige al login.

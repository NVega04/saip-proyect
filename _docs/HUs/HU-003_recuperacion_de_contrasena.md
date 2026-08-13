# HU-003 — Recuperación de contraseña

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-003 |
| Título | Recuperación de contraseña |
| Módulo | Autenticación |
| Prioridad | Alta |
| Estado | Completado |
| RF asociados | RF003 |

---

## Historia

Como usuario registrado, quiero recuperar mi contraseña en caso de olvido mediante un token de restablecimiento por correo electrónico, para poder volver a acceder al sistema de forma segura.

---

## Criterios de aceptación

### CA-003.1 — Solicitud de recuperación con correo registrado

**Dado** que ingreso mi correo electrónico registrado en el sistema,
**cuando** solicito la recuperación de contraseña,
**entonces** el sistema:
- Invalida cualquier token de restablecimiento previo no utilizado para ese usuario
- Genera un token seguro (`secrets.token_urlsafe(32)`)
- Crea un registro `PasswordReset` en base de datos con el token, asociado al usuario, con expiración a 30 minutos
- Envía un correo electrónico con un enlace de restablecimiento que incluye el token como parámetro
- Muestra el mensaje genérico "Si el correo está registrado, recibirás instrucciones."

### CA-003.2 — Correo no registrado

**Dado** que ingreso un correo que no existe en el sistema,
**cuando** solicito la recuperación,
**entonces** el sistema muestra el mismo mensaje genérico "Si el correo está registrado, recibirás instrucciones." sin revelar si el correo existe o no (protección contra enumeración de usuarios).

### CA-003.3 — Restablecimiento exitoso con token válido

**Dado** que tengo un enlace de restablecimiento con token válido (no expirado, no usado),
**cuando** ingreso una nueva contraseña y confirmo,
**entonces** el sistema:
- Verifica que el token exista, no esté usado y no haya expirado (30 min)
- Actualiza la contraseña del usuario cifrada con bcrypt
- Marca el token como usado (`used = true`)
- **Invalida todas las sesiones activas** del usuario por seguridad
- Muestra mensaje de éxito

### CA-003.4 — Token expirado

**Dado** que han pasado más de 30 minutos desde que solicité el restablecimiento,
**cuando** intento usar el enlace con el token,
**entonces** el sistema muestra el mensaje "El token ha expirado." y debo solicitar un nuevo restablecimiento.

### CA-003.5 — Token ya utilizado

**Dado** que ya utilicé el enlace de restablecimiento anteriormente,
**cuando** intento usar el mismo token nuevamente,
**entonces** el sistema muestra el mensaje "El token ya fue utilizado."

### CA-003.6 — Rate limiting en solicitudes de recuperación

**Dado** que realizo múltiples solicitudes de recuperación desde la misma IP,
**cuando** supero 3 solicitudes en un minuto,
**entonces** el sistema responde con error 429 (Too Many Requests).

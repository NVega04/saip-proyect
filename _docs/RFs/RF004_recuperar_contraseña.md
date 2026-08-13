# RF-004 — Recuperar contraseña

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-004 |
| **Nombre** | Recuperar contraseña |
| **Módulo** | Autenticación |
| **Prioridad** | Alta |
| **Estado** | Implementado |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe ofrecer a los usuarios registrados recuperar su contraseña en caso de olvido, mediante un token de restablecimiento de un solo uso con expiración de 30 minutos, enviado por correo electrónico.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `email` | Texto (email) | Sí | Formato de email válido |
| `token` | Texto | Sí (reset) | Debe existir, no estar usado y no haber expirado |
| `new_password` | Texto | Sí (reset) | Se hashea con bcrypt |

---

## Proceso

1. Usuario selecciona "Olvidé mi contraseña" desde el login.
2. Ingresa su correo y envía `POST /session/forgot-password`.
3. Backend (rate-limited: 3/min por IP):
   - Busca usuario por email.
   - Si existe y está activo: invalida tokens previos no usados, genera `secrets.token_urlsafe(32)`, crea `PasswordReset` con expiración 30 min.
   - Envía correo con enlace: `{FRONTEND_URL}/reset-password?token={token}`.
   - Responde con mensaje genérico (no revela si el correo existe).
4. Usuario accede al enlace, ingresa nueva contraseña.
5. Frontend envía `POST /session/reset-password` con `token` + `new_password`.
6. Backend:
   - Valida que el token exista, no esté usado y no haya expirado (30 min).
   - Hashea la nueva contraseña con bcrypt y actualiza el usuario.
   - Marca el token como usado (`used = true`).
   - **Invalida todas las sesiones activas** del usuario por seguridad.
   - Muestra mensaje de éxito.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Solicitud enviada (correo exista o no) | 200 | "Si el correo está registrado, recibirás instrucciones." |
| Token inválido | 400 | "Token inválido." |
| Token ya utilizado | 400 | "El token ya fue utilizado." |
| Token expirado | 400 | "El token ha expirado." |
| Contraseña actualizada | 200 | "Contraseña actualizada correctamente." |
| Demasiadas solicitudes | 429 | Rate limit exceeded (3/min por IP) |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| POST | `/session/forgot-password` | No | Solicitar recuperación (rate-limited: 3/min) |
| POST | `/session/reset-password` | No | Restablecer contraseña con token |

---

## Reglas de negocio

- **RN-019**: La respuesta de solicitud es genérica para evitar enumeración de usuarios.
- **RN-020**: Token de un solo uso con expiración de 30 minutos.
- **RN-021**: Al restablecer la contraseña, se invalidan todas las sesiones activas del usuario.
- **RN-022**: Contraseña hasheada con bcrypt.
- **RN-023**: Rate limiting: máximo 3 solicitudes de recuperación por minuto por IP.

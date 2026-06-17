# RF-002 — Inicio de sesión

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-002 |
| **Nombre** | Inicio de sesión |
| **Módulo** | Autenticación |
| **Prioridad** | Alta |
| **Estado** | Implementado |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe permitir que los usuarios accedan a la plataforma SAIP ingresando su correo electrónico y contraseña, mediante un esquema de autenticación **híbrido JWT + sesión en base de datos**.

### Arquitectura del token híbrido

1. **Login**: Backend verifica credenciales (bcrypt), invalida sesiones anteriores, crea `SessionApp` en BD con token UUID + expiración a 8h, firma un JWT (HS256) con el UUID interno como payload.
2. **Cliente**: Almacena el JWT en `localStorage` bajo `session_token`.
3. **Cada request**: Frontend envía JWT en header `session-token`. Backend decodifica JWT, extrae UUID, busca sesión en BD, verifica activa y vigente.
4. **Ventaja**: JWT garantiza integridad (firmado); BD permite revocación en servidor (logout, cambio de contraseña, desactivación).

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `email` | Texto (email) | Sí | Formato de email válido |
| `password` | Texto | Sí | No vacío |
| `accepted_terms` | Booleano | No | Si el usuario no ha aceptado términos, debe enviar `true` |

---

## Proceso

1. El usuario accede al formulario de inicio de sesión en `http://localhost:5173/login`.
2. Ingresa correo y contraseña.
3. Frontend envía `POST /session/login` con los datos.
4. Backend:
   - Busca usuario por email.
   - Verifica que esté activo (`status = active`).
   - Compara contraseña con bcrypt.
   - Si es primera vez o no ha aceptado términos, requiere `accepted_terms = true`.
   - Invalida sesiones activas anteriores (`is_active = false`).
   - Crea nueva sesión (`SessionApp` con token UUID, expira a 8h, `is_active = true`).
   - Genera JWT firmado con HS256 que contiene `session_token` (UUID) y `sub` (user_id).
   - Retorna `{ session_token: JWT, expires_at, user, modules }`.
5. Frontend almacena JWT en `localStorage`, módulos permitidos en `localStorage`, redirige al dashboard.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Inicio de sesión exitoso | 200 | `{ session_token: "(JWT)", expires_at, user, terms_required }` |
| Credenciales incorrectas | 401 | "Credenciales inválidas." |
| Cuenta inactiva | 403 | "El usuario está inactivo. Contacte al administrador." |
| Términos no aceptados | 403 | "Debe aceptar los términos y condiciones para continuar." |
| Demasiados intentos | 429 | Rate limit exceeded (5/min por IP) |
| Error interno | 500 | Mensaje genérico |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| POST | `/session/login` | No | Inicio de sesión (rate-limited: 5/min) |
| POST | `/session/logout` | Sí (JWT) | Cerrar sesión |
| POST | `/session/logout-all` | Sí (JWT) | Cerrar sesión en todos los dispositivos |

---

## Reglas de negocio

- **RN-007**: El acceso solo se concede si las credenciales coinciden y el usuario está activo.
- **RN-008**: La contraseña nunca se envía ni almacena en texto plano; siempre se compara mediante bcrypt.
- **RN-009**: En caso de credenciales incorrectas, el sistema no revela qué campo es incorrecto ("Credenciales inválidas.").
- **RN-010**: Se implementa rate limiting por IP: máximo 5 intentos de login por minuto.
- **RN-011**: Tras autenticación exitosa, se genera un JWT firmado HS256 con expiración a 8 horas.
- **RN-012**: El JWT no es suficiente por sí solo; cada request verifica la sesión en BD (is_active + expires_at).
- **RN-013**: Al iniciar sesión, se invalidan todas las sesiones activas anteriores del mismo usuario.
- **RN-014**: El usuario debe aceptar términos y condiciones al menos una vez.

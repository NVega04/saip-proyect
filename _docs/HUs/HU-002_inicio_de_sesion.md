# HU-002 — Inicio de sesión

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-002 |
| Título | Inicio de sesión |
| Módulo | Autenticación |
| Prioridad | Alta |
| Estado | Completado |
| RF asociados | RF002 |

---

## Historia

Como usuario registrado, quiero iniciar sesión con mis credenciales (correo y contraseña), para acceder al sistema de forma segura mediante un token híbrido JWT + sesión en base de datos.

---

## Arquitectura del token híbrido JWT + sesión

El sistema utiliza un esquema de autenticación híbrido que combina JWT (JSON Web Token) con sesiones persistentes en base de datos:

### Flujo de inicio de sesión

1. El usuario envía `email` + `password` a `POST /session/login`
2. El backend verifica: usuario existe, está activo, contraseña correcta (bcrypt), términos aceptados
3. Se invalidan todas las sesiones activas anteriores del mismo usuario (`is_active = false`)
4. Se crea un nuevo registro `SessionApp` en base de datos con:
   - `token`: UUID v4 único (identificador interno de sesión)
   - `user_id`: ID del usuario autenticado
   - `expires_at`: 8 horas desde la creación
   - `is_active`: true
5. Se genera un **JWT firmado con HS256** que contiene en su payload:
   - `sub`: ID del usuario
   - `session_token`: el UUID interno de la sesión
   - `exp`: timestamp de expiración
   - `iat`: timestamp de emisión
6. El frontend recibe `{ session_token: JWT, expires_at, user }` y almacena el JWT en `localStorage`

### Flujo en cada solicitud posterior

1. El frontend envía el JWT en el header `session-token` en cada petición
2. El backend:
   a. Decodifica y verifica la firma del JWT (HS256)
   b. Extrae el `session_token` (UUID interno) del payload
   c. Busca la sesión en BD por ese UUID
   d. Verifica que la sesión esté activa (`is_active = true`) y no haya expirado
   e. Devuelve el usuario asociado a la sesión

### Ventajas del esquema híbrido

| Capa | Beneficio |
|------|-----------|
| **JWT** | Integridad criptográfica (firmado), no modificable por el cliente, contiene metadatos legibles |
| **BD (sesión)** | Revocación inmediata en servidor (logout, cambio de contraseña, desactivación de cuenta), control de sesiones múltiples |

### Mecanismos que invalidan sesiones

- Cierre de sesión explícito (`POST /session/logout`)
- Cierre de sesión en todos los dispositivos (`POST /session/logout-all`)
- Nuevo inicio de sesión (invalida sesiones anteriores del mismo usuario)
- Restablecimiento de contraseña (invalida todas las sesiones activas)
- Desactivación de cuenta por administrador

---

## Criterios de aceptación

### CA-002.1 — Inicio de sesión exitoso

**Dado** que ingreso credenciales correctas (correo registrado y contraseña válida),
**cuando** inicio sesión,
**entonces** el sistema:
- Invalida sesiones activas anteriores del mismo usuario
- Crea una nueva sesión en BD con token UUID, expiración a 8 horas y estado activo
- Genera un JWT firmado con HS256 que encapsula el UUID de la sesión
- Almacena el JWT en `localStorage` del navegador bajo la clave `session_token`
- Me redirige al dashboard

### CA-002.2 — Credenciales inválidas

**Dado** que ingreso un correo no registrado o una contraseña incorrecta,
**cuando** intento iniciar sesión,
**entonces** el sistema responde con error 401 y el mensaje "Credenciales inválidas.", sin revelar si el correo existe o no.

### CA-002.3 — Usuario inactivo

**Dado** que mi cuenta ha sido desactivada por un administrador,
**cuando** intento iniciar sesión con credenciales correctas,
**entonces** el sistema responde con error 403 y el mensaje "El usuario está inactivo. Contacte al administrador."

### CA-002.4 — Aceptación de términos y condiciones

**Dado** que es mi primer inicio de sesión o no he aceptado los términos,
**cuando** intento iniciar sesión sin marcar la casilla de aceptación,
**entonces** el sistema responde con error 403 y el mensaje "Debe aceptar los términos y condiciones para continuar."
**Y** si marco la casilla y las credenciales son correctas, se registra la fecha de aceptación (`accepted_terms_at`) y se permite el acceso.

### CA-002.5 — Rate limiting en intentos de login

**Dado** que realizo múltiples intentos de inicio de sesión fallidos desde la misma IP,
**cuando** supero 5 intentos en un minuto,
**entonces** el sistema responde con error 429 (Too Many Requests) y bloquea temporalmente nuevos intentos desde esa IP.

### CA-002.6 — Protección de rutas por token

**Dado** que no tengo un token válido (nunca inicié sesión o el token expiró),
**cuando** intento acceder a una ruta protegida del frontend,
**entonces** el componente `ProtectedRoute` detecta que no hay token y me redirige a la página de inicio.
**Y** si el backend recibe un request con token inválido, responde 401 y el frontend limpia `localStorage` y redirige a `/`.

### CA-002.7 — Expiración de sesión

**Dado** que mi sesión ha superado las 8 horas de duración,
**cuando** intento realizar cualquier operación,
**entonces** el backend detecta que `expires_at` ha vencido, responde 401 con "Sesión expirada", y el frontend limpia el token y redirige al login.

### CA-002.8 — Permisos por módulo

**Dado** que inicio sesión correctamente,
**cuando** el backend procesa la autenticación,
**entonces** el frontend recibe y almacena en `localStorage` bajo la clave `modules` la lista de módulos a los que tiene acceso el rol del usuario, permitiendo o denegando visualización de secciones en la interfaz.

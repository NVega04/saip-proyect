# RF-005 — Cerrar sesión

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-005 |
| **Nombre** | Cerrar sesión |
| **Módulo** | Autenticación |
| **Prioridad** | Alta |
| **Estado** | Implementado |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe permitir a los usuarios autenticados cerrar su sesión de forma segura (individual o en todos los dispositivos), garantizando que la sesión activa se invalide en base de datos y que el JWT correspondiente quede inservible.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| (Ninguna) | - | - | La solicitud debe incluir el JWT válido en header `session-token` |

---

## Proceso

### Cierre de sesión individual

1. El usuario autenticado selecciona "Cerrar sesión" en la interfaz.
2. Frontend envía `POST /session/logout` con el JWT en header `session-token`.
3. Backend:
   - Decodifica el JWT y extrae el UUID interno de sesión.
   - Busca la sesión en BD por ese UUID.
   - Marca la sesión como `is_active = false`.
4. Frontend limpia `localStorage` y redirige a `/login`.

### Cierre de sesión en todos los dispositivos

1. El usuario selecciona "Cerrar sesión en todos los dispositivos".
2. Frontend envía `POST /session/logout-all`.
3. Backend:
   - Busca todas las sesiones activas del usuario.
   - Marca todas como `is_active = false`.
4. Frontend limpia `localStorage` y redirige a `/login`.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Cierre de sesión exitoso | 200 | "Sesión cerrada correctamente" |
| Cierre en todos los dispositivos | 200 | "Sesión cerrada en todos los dispositivos." |
| Token inválido | 401 | "Token inválido" |
| Sesión no encontrada | 404 | "Sesión no encontrada" |
| Error interno | 500 | Mensaje genérico |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| POST | `/session/logout` | Sí (JWT) | Cerrar sesión actual |
| POST | `/session/logout-all` | Sí (JWT) | Cerrar sesión en todos los dispositivos |

---

## Reglas de negocio

- **RN-024**: El cierre de sesión invalida la sesión en base de datos (`is_active = false`), no solo el token local.
- **RN-025**: No es posible reutilizar el JWT tras logout porque la sesión en BD está inactiva.
- **RN-026**: La opción de cerrar sesión debe estar disponible en todo momento (navbar).
- **RN-027**: Tras cierre exitoso, se redirige al login y se limpia `localStorage`.
- **RN-028**: Cualquier intento de acceder a recursos protegidos después de logout responde 401 y redirige al login.

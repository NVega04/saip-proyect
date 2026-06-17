# RF-003 — Cambio de contraseña

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-003 |
| **Nombre** | Cambio de contraseña |
| **Módulo** | Autenticación / Perfil |
| **Prioridad** | Alta |
| **Estado** | Implementado |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe permitir a los usuarios autenticados cambiar su contraseña actual por una nueva, verificando la identidad mediante la contraseña actual. Esta funcionalidad está disponible en la sección de perfil.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `current_password` | Texto | Sí | Debe coincidir con la contraseña actual almacenada (bcrypt) |
| `new_password` | Texto | Sí | Se hashea con bcrypt antes de almacenar |

---

## Proceso

1. El usuario autenticado accede a su perfil (`/perfil`) y selecciona "Cambiar contraseña".
2. Ingresa su contraseña actual y la nueva contraseña.
3. Frontend envía `POST /session/change-password` con el JWT en header `session-token`.
4. Backend:
   - Verifica que la contraseña actual coincida con el hash almacenado (bcrypt).
   - Hashea la nueva contraseña con bcrypt.
   - Actualiza `password_hash` y `updated_at` en el registro del usuario.
   - No invalida sesiones activas (el cambio de contraseña desde perfil no fuerza logout).
5. Muestra mensaje de éxito.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Cambio exitoso | 200 | "Contraseña actualizada correctamente." |
| Contraseña actual incorrecta | 400 | "La contraseña actual es incorrecta." |
| No autenticado | 401 | "Token inválido" / "Sesión expirada" |
| Error interno | 500 | Mensaje genérico |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| POST | `/session/change-password` | Sí (JWT) | Cambiar contraseña desde perfil |

---

## Reglas de negocio

- **RN-015**: El cambio de contraseña solo es posible para usuarios autenticados.
- **RN-016**: La contraseña actual debe coincidir exactamente con la almacenada (validación bcrypt).
- **RN-017**: La contraseña nunca se almacena en texto plano; siempre se hashea con bcrypt.
- **RN-018**: Mensajes de error claros sin revelar datos sensibles.

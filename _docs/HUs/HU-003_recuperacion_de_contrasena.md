# HU-003 — Recuperación de contraseña

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-003 |
| Título | Recuperación de contraseña |
| Módulo | Autenticación |
| Prioridad | Alta |
| Estado | Pendiente |
| RF asociados | RF003 |

---

## Historia

Como usuario registrado, quiero recuperar mi contraseña en caso de olvido, para poder volver a acceder al sistema.

---

## Criterios de aceptación

### CA-003.1 — Solicitud de recuperación
**Dado** que ingreso mi correo registrado,  
**cuando** solicito recuperación,  
**entonces** el sistema debe enviar un enlace de restablecimiento.

### CA-003.2 — Correo no registrado
**Dado** que ingreso un correo no existente,  
**cuando** solicito recuperación,  
**entonces** debo recibir mensaje de validación.
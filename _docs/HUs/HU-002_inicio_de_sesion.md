# HU-002 — Inicio de sesión

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-002 |
| Título | Inicio de sesión |
| Módulo | Autenticación |
| Prioridad | Alta |
| Estado | Pendiente |
| RF asociados | RF002 |

---

## Historia

Como usuario registrado, quiero iniciar sesión con mis credenciales, para acceder al sistema.

---

## Criterios de aceptación

### CA-002.1 — Acceso válido
**Dado** que ingreso credenciales correctas,  
**cuando** inicio sesión,  
**entonces** debo acceder al dashboard.

### CA-002.2 — Credenciales inválidas
**Dado** que ingreso datos incorrectos,  
**cuando** intento iniciar sesión,  
**entonces** debo visualizar un mensaje de error.
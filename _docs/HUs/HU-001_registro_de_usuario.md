# HU-001 — Registro de usuario

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-001 |
| Título | Registro de usuario |
| Módulo | Autenticación |
| Prioridad | Alta |
| Estado | Pendiente |
| RF asociados | RF001 |

## Historia

Como visitante del sistema, quiero registrarme con mis datos personales, para poder acceder a las funcionalidades del sistema.

## Criterios de aceptación

### CA-001.1 — Registro exitoso
**Dado** que ingreso datos válidos,  
**cuando** envío el formulario,  
**entonces** el usuario debe crearse correctamente.

### CA-001.2 — Validación de campos obligatorios
**Dado** que dejo campos obligatorios vacíos,  
**cuando** intento registrarme,  
**entonces** el sistema debe mostrar mensajes de validación.

### CA-001.3 — Usuario duplicado
**Dado** que el correo ya existe en el sistema,  
**cuando** intento registrarme,  
**entonces** el sistema debe impedir el registro y mostrar un mensaje de error.
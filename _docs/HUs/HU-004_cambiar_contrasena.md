# HU-004 — Cambiar contraseña

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-004 |
| Título | Cambiar contraseña |
| Módulo | Autenticación |
| Prioridad | Alta |
| Estado | Completado |
| RF asociados | RF004 |

---

## Historia

Como usuario autenticado, quiero cambiar mi contraseña desde el perfil, para mejorar la seguridad de mi cuenta sin necesidad de solicitar un restablecimiento.

---

## Criterios de aceptación

### CA-004.1 — Cambio exitoso con contraseña actual correcta

**Dado** que estoy autenticado en el sistema y accedo a la opción de cambiar contraseña,
**cuando** ingreso mi contraseña actual correctamente y registro una nueva contraseña válida,
**entonces** el sistema:
- Verifica que la contraseña actual coincida con el hash almacenado (bcrypt)
- Actualiza el hash de la contraseña con la nueva contraseña
- Registra auditoría (`updated_at`)
- Muestra mensaje de éxito

### CA-004.2 — Contraseña actual incorrecta

**Dado** que estoy autenticado y quiero cambiar mi contraseña,
**cuando** ingreso una contraseña actual que no coincide con la almacenada,
**entonces** el sistema muestra el mensaje "La contraseña actual es incorrecta." y no realiza el cambio.

### CA-004.3 — Protección por autenticación

**Dado** que no estoy autenticado (token inválido, expirado o inexistente),
**cuando** intento acceder al endpoint de cambio de contraseña,
**entonces** el sistema responde con error 401 (No autorizado).

### CA-004.4 — Persistencia del cambio

**Dado** que cambio mi contraseña exitosamente,
**cuando** cierro sesión y vuelvo a iniciar sesión,
**entonces** puedo acceder correctamente con la nueva contraseña y la anterior ya no es válida.

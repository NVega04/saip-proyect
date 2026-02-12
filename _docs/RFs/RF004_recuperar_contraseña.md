# RF-004 — Recuperar contraseña
<!--
  ¿Qué? Requisito funcional que permite a los usuarios recuperar su contraseña olvidada mediante verificación por correo.
  ¿Para qué? Documentar el flujo seguro de recuperación de acceso.
  ¿Impacto? Sin este requisito, usuarios con contraseña olvidada perderían acceso permanente al sistema.
-->
---
## Identificación
| Campo     | Valor                  |
|-----------|------------------------|
| **ID**    | RF-004                 |
| **Nombre**| Recuperar contraseña   |
| **Módulo**| Autenticación          |
| **Prioridad** | Alta               |
| **Estado**| Implementado           |
| **Fecha** | Febrero 2026           |
---
## Descripción
El sistema debe ofrecer a los usuarios registrados recuperar su contraseña en caso de olvido, mediante un proceso sencillo y seguro. El usuario solicita recuperación indicando su correo electrónico registrado. El sistema envía un enlace o código de verificación al correo, permitiendo establecer una nueva contraseña y restablecer el acceso a SAIP.
---
## Entradas
| Campo                  | Tipo          | Obligatorio | Validaciones                                                                 |
|------------------------|---------------|-------------|------------------------------------------------------------------------------|
| `email`                | Texto (email) | Sí          | Formato válido, máximo 255 caracteres                                        |
| `reset_token`          | Texto         | Sí (reset)  | Debe coincidir y estar vigente                                               |
| `new_password`         | Texto         | Sí (reset)  | Mínimo 8 caracteres, 1 mayúscula, 1 minúscula, 1 número                     |
| `confirm_new_password` | Texto         | Sí (reset)  | Coincidir con `new_password`                                                 |
---
## Proceso
1. Usuario selecciona "Olvidé mi contraseña".
2. Ingresa correo y envía solicitud.
3. Backend valida email y existencia de usuario.
4. Genera token único con expiración (30-60 min).
5. Envía correo con enlace o código.
6. Usuario accede al enlace/código.
7. Sistema valida token.
8. Usuario ingresa nueva contraseña y confirmación.
9. Backend valida fortaleza y coincidencia.
10. Hashea y actualiza contraseña.
11. Invalida token.
12. Mensaje de éxito y redirección a login.
---
## Salidas
| Escenario                              | Código HTTP | Respuesta                                                                 |
|----------------------------------------|-------------|---------------------------------------------------------------------------|
| Solicitud exitosa (enlace enviado)     | 200         | Mensaje: "Se ha enviado un enlace de recuperación"                        |
| Correo no registrado                   | 400         | Mensaje: "No existe usuario con ese correo"                               |
| Token inválido/expirado                | 400         | Mensaje: "Enlace inválido o expirado. Solicita uno nuevo"                 |
| Contraseña no cumple requisitos        | 422         | Detalle de errores                                                        |
| Contraseñas no coinciden               | 422         | Mensaje: "Las contraseñas no coinciden"                                   |
| Error interno                          | 500         | Mensaje genérico                                                          |
---
## Endpoint asociado
| Método | Ruta                                      | Auth requerida |
|--------|-------------------------------------------|----------------|
| POST   | `/api/v1/auth/forgot-password`            | No             |
| POST   | `/api/v1/auth/reset-password`             | No             |
---
## Reglas de negocio
- RN-023: Recuperación solo válida si el correo corresponde a usuario existente.
- RN-024: Enlace/código con tiempo de vigencia limitado (30-60 minutos).
- RN-025: Token de un solo uso; se invalida tras uso o expiración.
- RN-026: Nueva contraseña cumple criterios mínimos de fortaleza.
- RN-027: Contraseña hasheada con bcrypt.
- RN-028: Mensajes claros en errores (sin revelar info sensible).
- RN-029: Rate limiting en solicitudes de recuperación (máx. por hora/IP).
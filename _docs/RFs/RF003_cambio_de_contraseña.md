# RF-003 — Cambio de contraseña
<!--
  ¿Qué? Requisito funcional que permite a usuarios autenticados cambiar su contraseña actual por una nueva de forma segura.
  ¿Para qué? Documentar el flujo controlado de actualización de credenciales desde el perfil del usuario.
  ¿Impacto? Sin este requisito, los usuarios no podrían actualizar sus contraseñas de manera autónoma y segura, aumentando riesgos de exposición prolongada en caso de sospecha de compromiso.
-->
---
## Identificación
| Campo     | Valor                  |
|-----------|------------------------|
| **ID**    | RF-003                 |
| **Nombre**| Cambio de contraseña   |
| **Módulo**| Autenticación / Perfil |
| **Prioridad** | Alta               |
| **Estado**| Implementado           |
| **Fecha** | Febrero 2026           |
---
## Descripción
El sistema debe permitir a los usuarios autenticados cambiar su contraseña actual por una nueva. Esta funcionalidad debe estar disponible dentro del perfil del usuario o en una sección de configuración/seguridad de la cuenta, garantizando validación estricta de identidad y cumplimiento de políticas de seguridad.
---
## Entradas
| Campo                  | Tipo          | Obligatorio | Validaciones                                                                 |
|------------------------|---------------|-------------|------------------------------------------------------------------------------|
| `current_password`     | Texto         | Sí          | Debe coincidir con la contraseña actual almacenada (hasheada)               |
| `new_password`         | Texto         | Sí          | Mínimo 8 caracteres, al menos 1 mayúscula, 1 minúscula, 1 número, 1 carácter especial |
| `confirm_new_password` | Texto         | Sí          | Debe coincidir exactamente con `new_password`                                |
---
## Proceso
1. El usuario autenticado accede a la sección "Cambiar contraseña" en su perfil o configuración.
2. Ingresa su contraseña actual, la nueva contraseña y la confirmación.
3. El frontend realiza validaciones básicas y envía la solicitud al backend (con token de autenticación).
4. El backend valida los datos con Pydantic.
5. Verifica que la contraseña actual coincida exactamente con la almacenada (comparación bcrypt).
6. Valida que la nueva contraseña cumpla con la política de seguridad del sistema y no sea igual a la actual.
7. Verifica que la nueva contraseña y su confirmación coincidan.
8. Hashea la nueva contraseña con bcrypt.
9. Actualiza el campo de contraseña en el registro del usuario en la base de datos.
10. Registra el cambio en logs de auditoría.
11. Muestra mensaje de éxito.
---
## Salidas
| Escenario                              | Código HTTP | Respuesta                                                                 |
|----------------------------------------|-------------|---------------------------------------------------------------------------|
| Cambio de contraseña exitoso           | 200         | Mensaje: "Contraseña actualizada correctamente"                           |
| Contraseña actual incorrecta          | 400         | Mensaje: "La contraseña actual no coincide"                               |
| Nueva contraseña no cumple política    | 422         | Detalle de errores específicos                                            |
| Nuevas contraseñas no coinciden        | 422         | Mensaje: "Las contraseñas nuevas no coinciden"                            |
| Nueva contraseña igual a la actual     | 400         | Mensaje: "La nueva contraseña no puede ser igual a la actual"             |
| No autenticado                         | 401         | Mensaje: "Debes iniciar sesión para realizar esta acción"                 |
---
## Endpoint asociado
| Método | Ruta                                 | Auth requerida |
|--------|--------------------------------------|----------------|
| POST   | `/api/v1/auth/change-password`       | Sí (JWT)       |
---
## Reglas de negocio
- RN-015: El cambio de contraseña solo es posible para usuarios autenticados (token JWT válido).
- RN-016: La contraseña actual debe coincidir exactamente con la almacenada (validación bcrypt).
- RN-017: La nueva contraseña debe cumplir con la política de seguridad (mín. 8 caracteres, mayúsculas, minúsculas, números, caracteres especiales).
- RN-018: La nueva contraseña no puede ser igual a la contraseña actual.
- RN-019: Las dos contraseñas nuevas (nueva y confirmación) deben coincidir exactamente.
- RN-020: La contraseña nunca se almacena en texto plano; siempre se hashea con bcrypt.
- RN-021: Mensajes de error claros y específicos en caso de fallos (sin revelar datos sensibles).
- RN-022: Registrar cambio de contraseña en logs de auditoría (user_id, timestamp, IP).
# RF-001 — Registro de usuario
<!--
  ¿Qué? Requisito funcional que define el registro de nuevos usuarios en el sistema SAIP.
  ¿Para qué? Permitir la creación estandarizada de cuentas para acceder al sistema administrativo de productos.
  ¿Impacto? Sin este requisito, los usuarios no podrían incorporarse al sistema de forma segura y controlada.
-->
---
## Identificación
| Campo     | Valor                  |
|-----------|------------------------|
| **ID**    | RF-001                 |
| **Nombre**| Registro de usuario    |
| **Módulo**| Autenticación          |
| **Prioridad** | Alta               |
| **Estado**| Pendiente / En análisis |
| **Fecha** | Septiembre 2025        |
---
## Descripción
El sistema debe permitir a los usuarios registrarse creando una cuenta con datos básicos (nombre completo, correo electrónico, usuario y contraseña), para posteriormente poder iniciar sesión y acceder a las funcionalidades del software SAIP (Sistema Administrativo Integral de Productos).
---
## Entradas
| Campo          | Tipo          | Obligatorio | Validaciones                                                                 |
|----------------|---------------|-------------|------------------------------------------------------------------------------|
| `full_name`    | Texto         | Sí          | Mínimo 2 caracteres, máximo 255 caracteres                                   |
| `username`     | Texto         | Sí          | Único en el sistema, sin espacios, caracteres alfanuméricos + guiones bajos  |
| `email`        | Texto (email) | Sí          | Formato de email válido, máximo 255 caracteres, debe ser único en el sistema |
| `password`     | Texto         | Sí          | Mínimo 8 caracteres, al menos 1 mayúscula, 1 minúscula y 1 número           |
| `confirm_password` | Texto     | Sí          | Debe coincidir exactamente con `password`                                    |
---
## Proceso
1. El usuario accede al formulario de registro en la interfaz (web o app).
2. Completa los campos: nombre completo, nombre de usuario, correo electrónico, contraseña y confirmación.
3. El frontend realiza validaciones básicas (longitudes, formato email, coincidencia de contraseñas).
4. Se envía la solicitud POST al backend.
5. El backend valida los datos con Pydantic (formatos, longitudes, fortaleza de contraseña).
6. Verifica que el `email` y `username` no estén registrados previamente.
7. Hashea la contraseña con bcrypt antes de almacenarla.
8. Crea el registro del usuario en la tabla `users` (o equivalente) con estado inicial activo o pendiente según política.
9. Retorna los datos del usuario creado (sin contraseña ni datos sensibles).
---
## Salidas
| Escenario                  | Código HTTP | Respuesta                                                                 |
|----------------------------|-------------|---------------------------------------------------------------------------|
| Registro exitoso           | 201         | Datos del usuario creado (`id`, `username`, `email`, `full_name`, `created_at`, etc.) |
| Email ya registrado        | 400         | Mensaje: "El correo electrónico ya está registrado"                       |
| Username ya registrado     | 400         | Mensaje: "El nombre de usuario ya está en uso"                            |
| Datos inválidos / validación fallida | 422 | Detalle de errores por campo (ej: "password: debe contener al menos una mayúscula") |
| Error interno              | 500         | Mensaje genérico: "Error al procesar el registro"                         |
---
## Endpoint asociado
| Método | Ruta                           | Auth requerida |
|--------|--------------------------------|----------------|
| POST   | `/api/v1/auth/register`        | No             |
---
## Reglas de negocio
- RN-001: El correo electrónico debe ser único en todo el sistema.
- RN-002: El nombre de usuario (`username`) debe ser único y no puede contener espacios ni caracteres especiales no permitidos.
- RN-003: La contraseña nunca se almacena en texto plano; siempre se hashea con bcrypt.
- RN-004: La contraseña debe cumplir los requisitos mínimos de fortaleza (mínimo 8 caracteres, 1 mayúscula, 1 minúscula, 1 número).
- RN-005: El sistema debe impedir registros duplicados por correo o usuario.
- RN-006: La información personal se almacena de manera segura (cifrada/hasheada donde aplique).
- RN-007: Opcional: Enviar notificación de confirmación (correo o mensaje interno) tras registro exitoso.
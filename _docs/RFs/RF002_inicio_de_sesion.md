# RF-002 — Inicio de sesión
<!--
  ¿Qué? Requisito funcional que permite a los usuarios registrados autenticarse en la plataforma SAIP ingresando credenciales válidas.
  ¿Para qué? Documentar el proceso seguro de login que garantiza identificación única y acceso controlado a información y funcionalidades.
  ¿Impacto? Sin este requisito, no se podría controlar el acceso, comprometiendo la seguridad, integridad de datos y trazabilidad de acciones en el sistema.
-->
---
## Identificación
| Campo     | Valor                  |
|-----------|------------------------|
| **ID**    | RF-002                 |
| **Nombre**| Inicio de sesión       |
| **Módulo**| Autenticación          |
| **Prioridad** | Alta               |
| **Estado**| Implementado           |
| **Fecha** | Febrero 2026           |
---
## Descripción
El sistema debe permitir que los usuarios accedan a la plataforma SAIP ingresando su correo electrónico (o usuario) junto con una contraseña válida. Esta funcionalidad garantiza que cada persona se identifique de manera segura y acceda únicamente a la información y opciones que le corresponden dentro del sistema, protegiendo los datos sensibles y aplicando controles de seguridad.
---
## Entradas
| Campo     | Tipo          | Obligatorio | Validaciones                                      |
|-----------|---------------|-------------|---------------------------------------------------|
| `email` o `username` | Texto (email o alfanumérico) | Sí | Formato válido según tipo (email RFC o username sin espacios), máximo 255 caracteres |
| `password`| Texto         | Sí          | No vacío (validación de longitud y formato básica en frontend) |
---
## Proceso
1. El usuario accede al formulario de inicio de sesión en la interfaz (web o app).
2. Ingresa su correo electrónico (o username) y contraseña.
3. El frontend realiza validaciones básicas (campos no vacíos, formato de email si aplica) y envía POST al backend.
4. El backend valida los datos con Pydantic.
5. Busca el usuario por email o username en la base de datos.
6. Si existe, compara la contraseña proporcionada (hasheada con bcrypt) contra la almacenada.
7. Verifica que el usuario esté activo (`is_active = true`).
8. Si todo coincide, genera un token de acceso (JWT) con claims relevantes (user_id, roles, exp, etc.).
9. Registra el intento exitoso (log de auditoría).
10. Retorna el token y datos básicos del usuario (sin información sensible).
11. En caso de fallo: registra intento fallido, aplica rate limiting si supera umbral, y retorna error sin revelar detalles sensibles.
---
## Salidas
| Escenario                  | Código HTTP | Respuesta                                                                 |
|----------------------------|-------------|---------------------------------------------------------------------------|
| Inicio de sesión exitoso   | 200         | `{ "access_token": "...", "token_type": "bearer", "user": {id, email, full_name, roles, ...} }` |
| Credenciales incorrectas   | 401         | Mensaje: "Credenciales inválidas" (sin especificar si es email o contraseña) |
| Cuenta inactiva/bloqueada  | 403         | Mensaje: "Cuenta inactiva o bloqueada temporalmente. Contacta al administrador" |
| Datos inválidos (validación) | 422       | Detalle de errores por campo                                              |
| Demasiados intentos fallidos | 429     | Mensaje: "Demasiados intentos. Intenta nuevamente en X minutos"           |
| Error interno              | 500         | Mensaje genérico: "Error al procesar la solicitud"                        |
---
## Endpoint asociado
| Método | Ruta                       | Auth requerida |
|--------|----------------------------|----------------|
| POST   | `/api/v1/auth/login`       | No             |
---
## Reglas de negocio
- RN-008: El acceso al sistema solo se concede si las credenciales (email/username + contraseña) coinciden exactamente con las almacenadas en la base de datos y el usuario está activo.
- RN-009: La contraseña nunca se envía ni almacena en texto plano; siempre se compara mediante hash bcrypt.
- RN-010: En caso de credenciales incorrectas, el sistema no revela detalles sensibles (ej. "usuario no existe" vs "contraseña incorrecta") para evitar enumeración de cuentas.
- RN-011: Se implementa rate limiting por IP o por cuenta (ej. máximo 5-10 intentos fallidos en 15 minutos) para prevenir ataques de fuerza bruta.
- RN-012: Tras autenticación exitosa, se genera un token JWT con expiración corta (ej. 30-60 minutos) y se asocian roles/permisos para control de acceso posterior.
- RN-013: Se registra cada intento de login (exitoso o fallido) en logs de auditoría con timestamp, IP y user-agent para trazabilidad y detección de anomalías.
- RN-014: Una vez autenticado, el usuario accede únicamente a funcionalidades y datos permitidos por sus roles establecidos en el sistema.
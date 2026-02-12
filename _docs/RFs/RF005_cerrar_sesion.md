# RF-005 — Cerrar sesión
<!--
  ¿Qué? Requisito funcional que permite a los usuarios autenticados finalizar su sesión de forma segura en la plataforma SAIP.
  ¿Para qué? Documentar el proceso de logout que invalida la sesión activa y protege contra accesos no autorizados en el mismo dispositivo.
  ¿Impacto? Sin este requisito, las sesiones permanecerían abiertas indefinidamente, exponiendo el sistema a riesgos de acceso no autorizado si el dispositivo es compartido o robado.
-->
---
## Identificación
| Campo     | Valor                  |
|-----------|------------------------|
| **ID**    | RF-005                 |
| **Nombre**| Cerrar sesión          |
| **Módulo**| Autenticación          |
| **Prioridad** | Alta               |
| **Estado**| Implementado           |
| **Fecha** | Febrero 2026           |
---
## Descripción
El sistema debe permitir a los usuarios autenticados cerrar su sesión de forma segura, garantizando que la sesión activa se invalide correctamente y se eliminen los datos temporales asociados (como tokens). Esta funcionalidad asegura que, una vez cerrada la sesión, ninguna otra persona pueda interactuar con el sistema desde el mismo dispositivo sin volver a autenticarse.
---
## Entradas
| Campo          | Tipo          | Obligatorio | Validaciones                                      |
|----------------|---------------|-------------|---------------------------------------------------|
| (Ninguna entrada adicional del usuario) | -     | -           | La solicitud debe ir acompañada del token JWT válido en el header Authorization |
---
## Proceso
1. El usuario autenticado selecciona la opción "Cerrar sesión" (botón o enlace en el menú de perfil/header).
2. El frontend envía una solicitud POST al backend (con el token JWT en el header).
3. El backend valida que el token sea válido y no haya expirado.
4. Invalida el token de acceso actual (blacklist en BD o Redis si aplica, o simplemente deja que expire naturalmente si es stateless con corta expiración).
5. Elimina cualquier dato de sesión temporal asociado (cookies de sesión si aplica, refresh tokens si se usan).
6. Registra el evento de logout en logs de auditoría (user_id, timestamp, IP, user-agent).
7. Retorna respuesta de éxito.
8. El frontend elimina tokens locales (localStorage/sessionStorage), limpia caché relevante y redirige al usuario a la página de login.
9. Impide navegación hacia atrás (usando history.replaceState o similar) para evitar acceso a vistas protegidas desde caché del navegador.
10. Cualquier intento posterior de acceder a recursos protegidos sin nuevo login debe fallar con 401/403.
---
## Salidas
| Escenario                              | Código HTTP | Respuesta                                                                 |
|----------------------------------------|-------------|---------------------------------------------------------------------------|
| Cierre de sesión exitoso               | 200         | Mensaje: "Sesión cerrada correctamente" o vacío (204 No Content)          |
| Token inválido/expirado/no proporcionado | 401      | Mensaje: "No autorizado" o redirección implícita a login                  |
| Error interno                          | 500         | Mensaje genérico: "Error al procesar la solicitud"                        |
---
## Endpoint asociado
| Método | Ruta                       | Auth requerida |
|--------|----------------------------|----------------|
| POST   | `/api/v1/auth/logout`      | Sí (JWT)       |
---
## Reglas de negocio
- RN-030: El cierre de sesión invalida inmediatamente el token de acceso activo en el servidor (mediante blacklist o invalidación si es necesario).
- RN-031: No debe ser posible reutilizar el token o credenciales anteriores tras logout sin una nueva autenticación completa.
- RN-032: El sistema no permite regresar a pantallas protegidas mediante el botón "atrás" del navegador o caché local (implementar medidas como no-cache headers y history manipulation).
- RN-033: La opción de cerrar sesión debe estar disponible en todo momento para el usuario autenticado (en header, menú de perfil, etc.).
- RN-034: Tras cierre exitoso, redirigir siempre a la página de login con mensaje de confirmación claro: "Has cerrado sesión correctamente".
- RN-035: Cualquier intento de acceder a recursos protegidos después de logout debe ser rechazado con código 401/403 y mensaje que obligue a iniciar sesión nuevamente.
- RN-036: Registrar el evento de cierre de sesión en logs de auditoría con detalles mínimos (user_id, timestamp, IP, dispositivo aproximado) para trazabilidad y detección de anomalías.
- RN-037: Si se usan refresh tokens, invalidarlos también durante el logout para evitar sesiones persistentes.
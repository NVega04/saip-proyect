# RNF-001 — Seguridad

<!--
  ¿Qué? Requisito no funcional que define los estándares de seguridad del sistema.
  ¿Para qué? Garantizar que los datos sensibles (usuarios, inventario, ventas, recetas) estén protegidos contra accesos no autorizados y ataques comunes.
  ¿Impacto? Un fallo podría exponer información de inventario, producción, ventas o datos personales de usuarios y proveedores.
-->

## Identificación

| Campo             | Valor                                                  |
| ----------------- | ------------------------------------------------------ |
| **ID**            | RNF-001                                                |
| **Nombre**        | Seguridad                                              |
| **Categoría**     | Seguridad de la información                            |
| **Prioridad**     | Crítica                                                |
| **Estado**        | En proceso / Pendiente de implementación               |

## Requisitos

### RNF-001.1 — Autenticación obligatoria y cierre de sesión

Todo acceso a funcionalidades del sistema (excepto páginas públicas) requiere autenticación válida.  
Debe existir opción para cerrar sesión y, opcionalmente, cerrar todas las sesiones abiertas del usuario.

### RNF-001.2 — Almacenamiento seguro de contraseñas

Las contraseñas deben almacenarse exclusivamente mediante hashing con algoritmo **bcrypt** (o Argon2 si se prefiere).  
Nunca se almacenan en texto plano, ni se exponen en logs, respuestas API o backups.

### RNF-001.3 — Proceso de recuperación de contraseña

El sistema debe permitir recuperación de contraseña mediante envío de token/enlace temporal a correo verificado.

- Token válido máximo 60 minutos  
- Uso único  
- Mensaje genérico que no revele si el correo está registrado

### RNF-001.4 — Autorización basada en roles (RBAC)

Implementar control de acceso por roles:  

- Administrador: acceso total  
- Producción: gestión de insumos, recetas y producción  
- Ventas: registro de ventas y consulta de stock de productos terminados  
- Consulta: solo vistas de inventario y reportes (sin modificaciones)  
Verificación obligatoria en backend para cada endpoint sensible.

### RNF-001.5 — Protección contra ataques comunes

- Prevención de **SQL Injection** mediante uso exclusivo de ORM (SQLAlchemy u equivalente)  
- Protección contra **XSS** y **CSRF** (tokens anti-CSRF en formularios)  
- Mensajes de error genéricos en login y recuperación

### RNF-001.6 — Comunicación cifrada

Todas las comunicaciones entre frontend y backend deben realizarse mediante **HTTPS**.  

- TLS 1.2 o superior  
- HSTS activado en producción  
- Nunca permitir HTTP

### RNF-001.7 — Manejo seguro de variables sensibles

Credenciales, claves secretas (JWT, BD, SMTP, etc.) deben almacenarse en variables de entorno o archivo `.env` no versionado.  
Proveer `.env.example` como plantilla.

# Seguridad y operación de SAIP

Este documento describe las medidas de seguridad **implementadas** y los
procedimientos operativos (secretos, respaldo, restauración). Lo que aún no
está cubierto se enumera en [`PENDIENTES.md`](./PENDIENTES.md).

## Autenticación y sesiones

- El login valida credenciales con **bcrypt** y emite un **JWT** firmado con
  `JWT_SECRET` (algoritmo `HS256`). El token se envía en el header
  `session-token` y el frontend lo guarda en `localStorage`.
- Duración de la sesión: **8 horas** (`session_duration_hours`). Al expirar,
  el API responde 401 y el frontend redirige al login.
- `POST /session/logout` cierra la sesión actual; `POST /session/logout-all`
  invalida todas las sesiones del usuario.
- Solo son públicos `GET /health`, `POST /session/login`,
  `POST /session/forgot-password` y `POST /session/reset-password`. El resto de
  rutas exige sesión; la creación de usuarios y la consulta de auditoría exigen
  además permiso de administrador.

### Bloqueo por intentos fallidos

| Parámetro | Valor |
|-----------|-------|
| Intentos fallidos antes de bloquear | 3 (`MAX_LOGIN_ATTEMPTS`) |
| Duración del bloqueo | 3 minutos (`LOCK_DURATION_MINUTES`) |
| Respuesta HTTP | 423 con minutos restantes |

El contador se reinicia tras un login correcto o al vencer el bloqueo.

### Rate limiting

Implementado con SlowAPI. El middleware global aplica
`RATE_LIMIT_DEFAULT=100/minute` por IP a **todas** las rutas; las operaciones
sensibles tienen límites más estrictos:

| Endpoint | Límite |
|----------|--------|
| Global (todas las rutas) | 100 peticiones/minuto (`RATE_LIMIT_DEFAULT`) |
| `POST /session/login` | 5 peticiones/minuto |
| `POST /session/forgot-password` | 3 peticiones/minuto |
| `POST /users/` | 10 peticiones/minuto |
| Reportes y exportaciones (inventario, producción, ventas, reportes) | 5 peticiones/minuto |

El exceso devuelve **429** con `Retry-After`. `X-Forwarded-For` solo se tiene
en cuenta cuando la petición llega desde una IP declarada en
`TRUSTED_PROXY_HOSTS`; en cualquier otro caso se usa la IP de la conexión para
no permitir suplantación. Detalles de despliegue en
[`DEPLOY-SEGURIDAD.md`](./DEPLOY-SEGURIDAD.md).

Los reportes de `sessions` y `production` exigen rango de fechas (máximo 366
días) y todas las consultas están topadas en `REPORT_ROW_LIMIT=5000` filas; la
respuesta JSON indica `truncado: true` cuando se alcanza el tope.

La recuperación de contraseña devuelve **siempre el mismo mensaje** aunque el
correo no exista o la cuenta esté inactiva (evita enumeración de usuarios). Los
tokens de reseteo anteriores se invalidan al generar uno nuevo y expiran a los
**30 minutos** (`PASSWORD_RESET_EXPIRE_MINUTES`); son de un solo uso.

## Política de contraseñas

La misma política se aplica en el backend (`src/core/password.py`) y se
explica al usuario en el frontend (`passwordStrength.ts`):

- Mínimo **12 caracteres**.
- Al menos una **mayúscula**, una **minúscula**, un **número** y un
  **carácter especial**.

Una contraseña que no cumpla los criterios devuelve 400 con el detalle de los
requisitos incumplidos. Nunca se almacena en claro: solo el hash bcrypt
(`password_hash`). Ni la contraseña ni los tokens aparecen en logs ni en
auditoría (ver más abajo).

## Control de acceso (RBAC)

- Cada usuario pertenece a un **rol** y el rol tiene asignados **módulos**
  (`role_modules`). Las rutas sensibles usan `require_module("...")`, p. ej.
  anular ventas exige el módulo `sales` y los reportes de inventario el módulo
  `inventory`.
- `is_admin` habilita operaciones de administración (creación de usuarios,
  asignación de módulos, consulta de auditoría).
- La asignación de módulos solo la puede hacer un administrador.

## Secretos y variables sensibles

- `JWT_SECRET`, `FRONTEND_URL` y `ENCRYPTION_KEY` **deben** venir del entorno:
  la aplicación falla al arrancar si faltan. `JWT_SECRET` exige mínimo 32
  caracteres; `ENCRYPTION_KEY` es una lista CSV de claves Fernet de 32 bytes.
- Genera un secreto con:

  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(64))"
  ```

- **Nunca versiones `.env`**. En el repositorio solo existe `.env.example`.
- Si el secreto pudo filtrarse o se usó el valor de ejemplo, **rótalo**:

  1. Genera el valor nuevo y actualízalo en el gestor de secretos / `.env`.
  2. Reinicia el backend (`docker compose up -d --force-recreate backend`).
  3. Todas las sesiones activas quedan invalidadas; los usuarios vuelven a
     iniciar sesión.

- Usa una **contraseña de aplicación** de SMTP, nunca la contraseña real de la
  cuenta de correo. En producción prefiere un gestor de secretos (Vault, AWS
  Secrets Manager, etc.) sobre variables planas.

## Cifrado en reposo

El NIT de proveedores y el teléfono de usuarios se almacenan cifrados con
Fernet (`src/core/crypto.py`), aplicado como `TypeDecorator` en el modelo.
Para poder buscar por NIT sin descifrar toda la tabla se guarda además un
índice ciego HMAC normalizado (`nit_hash`); la búsqueda usa ese índice y el
NIT en claro nunca vuelve a la base de datos.

- La migración `6ef9e1aec914` cifra los valores existentes y calcula el
  índice ciego; `downgrade -1` revierte el proceso.
- `ENCRYPTION_KEY` admite rotación: `nueva,anterior`. La primera clave cifra;
  todas pueden descifrar. **Perder las claves antiguas impide leer los datos
  cifrados**: guárdalas en un gestor de secretos y haz respaldos de ellas.
- La auditoría elimina también `nit`, `phone`, `telefono` y `celular` de los
  valores registrados.

## CORS y HTTPS

- `CORS_ORIGINS` es una lista separada por coma. La configuración rechaza
  comodines (`*`) y exige esquema `http://` o `https://`.
- Producción debe servir el frontend por **HTTPS** y terminar TLS en un reverse
  proxy; `CORS_ORIGINS` debe contener solo el dominio HTTPS. La DB no expone
  puertos al host en `docker-compose.prod.yml`.
- Configura HSTS y las cabeceras de seguridad siguiendo
  [`DEPLOY-SEGURIDAD.md`](./DEPLOY-SEGURIDAD.md) y el ejemplo
  `docs/examples/nginx-saip.conf`. Activa HSTS solo después de verificar HTTPS
  en todo el dominio.

## Auditoría

- La tabla `audit_log` (migración `898807c7b86f`) registra acción, tipo/id de
  recurso, valores anteriores y nuevos, `user_id`, IP y timestamp.
- Es de solo lectura desde la API (`GET /audit/`, solo administradores).
- Antes de guardarse, `sanitize_audit_value` elimina de forma recursiva
  cualquier clave que coincida con `password|passwd|secret|token|hash|jwt|
  credential|authorization|reset|nit|phone|telefono|celular`. Contraseñas,
  tokens, NIT y teléfonos **nunca** se escriben en la auditoría.

## Logging

- `src/core/logging.py` configura logs **JSON estructurados** por defecto
  (`LOG_FORMAT=json`), con un `X-Request-ID` por petición
  (`RequestIdMiddleware`) y `LOG_LEVEL=INFO` por defecto.
- `RedactionFilter` enmascara contraseñas, tokens (incluidos JWT y
  `Bearer ...`), secretos y claves de API en cualquier mensaje de log.
- `SQLALCHEMY_ECHO` está desactivado por defecto; activarlo implica que las
  sentencias SQL (sin contraseñas) se registrarán: solo para depuración
  puntual y nunca en producción.

## Respaldo y restauración

Hay scripts reproducibles en `scripts/` (programar su ejecución sigue siendo
responsabilidad del operador):

```bash
# Respaldo lógico comprimido con retención de 7 días
./scripts/backup_db.sh

# Restauración en una BD distinta; TARGET_DB por defecto es un nombre *_restore
TARGET_DB=db_saip_restore ./scripts/restore_db.sh backups/db_saip_proyect_*.sql.gz

# Tras restaurar, asegurar el esquema al-head y reiniciar el backend
cd backend && uv run alembic upgrade head
```

`BACKUP_DIR` y `RETENTION_DAYS` son configurables. Los volcados contienen
datos cifrados (NIT/teléfonos) y hashes de contraseñas, nunca secretos en
claro. No ejecutar la restauración sobre la base de producción sin antes
verificarla en staging. Procedimiento detallado en
[`DEPLOY-SEGURIDAD.md`](./DEPLOY-SEGURIDAD.md).

Buenas prácticas:

- Programar el respaldo con cron en el host y conservar varias rotaciones.
- Guardar los volcados cifrados y fuera del servidor de aplicación.
- **Probar la restauración periódicamente** en un entorno de staging.
- Coordinar la rotación de `JWT_SECRET` con la restauración: al restaurar una
  DB antigua, las sesiones emitidas con un secreto distinto dejarán de ser
  válidas (esperado).

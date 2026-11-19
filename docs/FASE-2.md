# Fase 2 — Seguridad P0

Rama: `fase-2-seguridad-p0` (desde `master` con la deriva de Alembic ya
cerrada en `fase-1-cierre-alembic`). No se leyó ni modificó `.env`, no se
tocaron migraciones aplicadas y el snapshot OpenAPI quedó intacto.

## Cambios por commit

1. `fix(config): endurecer variables de seguridad`
   - `jwt_secret` obligatorio con mínimo de 32 caracteres.
   - `sqlalchemy_echo=False` por defecto.
   - `cors_origins` leído de `CORS_ORIGINS` (CSV), normalizado (sin barras
     finales, sin duplicados, sin comodines y solo `http://`/`https://`).
   - `frontend_url` obligatorio y normalizado; helper `frontend_link(path)`
     para construir todos los enlaces.
   - `tests/conftest.py` define valores falsos para CI antes de importar
     `src.*`; 7 tests nuevos de configuración, incluido el arranque fallido
     sin `JWT_SECRET`.
2. `fix(security): eliminar secreto JWT por defecto`
   - `core/security.py` usa el secreto de `Settings`, sin fallback.
   - 4 tests de firma, verificación, token manipulado y secreto ajeno.
3. `fix(cors): orígenes configurables por entorno`
   - `main.py` usa `settings.cors_origins`. Desaparecieron la IP HTTP,
     `localhost:8081`, `exp://*` y `https://saip.lat/`.
   - 4 tests de preflight (origen permitido, desconocido, con barra final y
     sin comodines).
4. `fix(security): validar contraseñas en backend`
   - `core/password.py`: política de 12 caracteres, mayúscula, minúscula,
     número y carácter especial, con los mismos mensajes del frontend.
   - Aplicada con `field_validator` en reset y cambio de contraseña (sin
     cambiar el OpenAPI) y a nivel de servicio como segunda barrera.
   - 6 tests, incluido el rechazo 422 del endpoint.
5. `fix(security): proteger contraseñas temporales`
   - `generate_temp_password()` genera 14 caracteres aleatorios que pasan el
     validador; se eliminó el log que imprimía la contraseña en claro.
   - 2 tests (cumplimiento de política y ausencia de la contraseña en logs).
6. `fix(frontend): alinear validador de contraseñas`
   - `passwordStrength.ts` usa los 5 criterios y expone
     `PASSWORD_POLICY_MESSAGE`; `Profilemodal` y `RecoverPassword` muestran el
     mismo mensaje. ESLint limpio en los archivos tocados.
7. `fix(email): configurar enlaces y manejo de SMTP`
   - `email.py` construye el login desde `FRONTEND_URL`, escapa valores HTML,
     centraliza el envío y registra fallos SMTP con `logger.exception` sin
     credenciales. Reseteo usa `settings.frontend_link(...)`.
   - `.env.example` documenta `JWT_SECRET` (con comando de generación y nota
     de rotación), `CORS_ORIGINS`, `SQLALCHEMY_ECHO=false`, `FRONTEND_URL` y
     el uso de contraseña de aplicación SMTP / gestor de secretos.
   - 4 tests de correo (sin links hardcodeados, link de bienvenida, link de
     reseteo y fallo SMTP sin filtrar la contraseña).

## Búsqueda de SQL concatenado (criterio 2.3)

No se encontró ningún `text(f"...")`, `.execute(f"...")` ni consulta construida
por f-strings en `backend/src` ni en `backend/alembic`. El único SQL crudo es
`text("SELECT 1")`, estático, en el healthcheck de base de datos.

## Verificación

| Comprobación | Resultado |
|---|---|
| `uv run pytest -q -p no:warnings -p no:cacheprovider` | **254 passed** (227 previos + 27 nuevos), ~38 s |
| `uv run alembic check` | `No new upgrade operations detected.` |
| Snapshot OpenAPI | Sin cambios; SHA-256 `3f2bc1bef68fca4138e88d4abd996c7fafbd02958e1f08f948a6eeb3f1295902` |
| `docker compose config -q` y `-f docker-compose.prod.yml` | OK |
| Preflight real (`uvicorn` temporal con las nuevas variables) | `localhost:5173` y `saip.lat` → 200; `saip.lat/`, `exp://*`, IP HTTP → 400 |
| ESLint de archivos frontend tocados | 0 errores (los 16 errores del repo son preexistentes y están fuera de estos archivos) |
| `tsc --noEmit` | 11 errores preexistentes, sin incrementos |

## Acción pendiente del desarrollador

Agregar `JWT_SECRET` a `.env` con un valor aleatorio de al menos 32 caracteres:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Después reiniciar el backend. Si en algún entorno real se llegó a usar el valor
por defecto `cambiar-en-produccion`, hay que rotar el secreto: las sesiones
activas quedarán invalidadas, lo cual es lo esperado.

Fuera de alcance de esta fase (queda documentado en `INVENTARIO.md`): el alias
`session_token` de `POST /session/logout`, que no está permitido por CORS.

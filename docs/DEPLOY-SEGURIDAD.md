# Despliegue seguro (Fase 3)

Este documento es una guía de referencia. **No sustituye la configuración real
del servidor ni modifica `docker-compose.prod.yml`.**

## Variables nuevas

| Variable | Default | Uso |
|---|---|---|
| `ENCRYPTION_KEY` | obligatoria | Claves Fernet CSV para cifrar NIT y teléfonos. La primera cifra; todas descifran. |
| `RATE_LIMIT_DEFAULT` | `100/minute` | Límite global por IP. |
| `TRUSTED_PROXY_HOSTS` | vacío | IPs desde las que se acepta `X-Forwarded-For`. Vacío = se usa la IP de conexión. |

Generar la clave de cifrado:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Para rotar, anteponer la clave nueva: `ENCRYPTION_KEY=nueva,anterior`. Guardar
siempre ambas en un gestor de secretos: perderlas impide leer los datos cifrados.

## TLS y HSTS

`docs/examples/nginx-saip.conf` es un ejemplo con redirección 80 → 443, TLS
1.2/1.3, HSTS y cabeceras de seguridad. Antes de activar HSTS, verificar que
HTTPS funciona en todo el dominio: el valor `max-age` es difícil de revertir.

El backend solo confía en `X-Forwarded-For` cuando la petición viene de una IP
declarada en `TRUSTED_PROXY_HOSTS`. Con nginx en el mismo host:

```bash
TRUSTED_PROXY_HOSTS=127.0.0.1,::1
```

Si el proxy está en otra máquina, declarar su IP. Nunca dejar la lista vacía si
se necesita la IP real del cliente detrás de un proxy.

## Respaldo y restauración

Scripts en `scripts/`:

```bash
# Respaldo con retención de 7 días (BACKUP_DIR y RETENTION_DAYS son configurables)
./scripts/backup_db.sh

# Restauración en una BD distinta (nunca sobre la de producción sin verificar)
TARGET_DB=db_saip_restore ./scripts/restore_db.sh backups/db_saip_proyect_*.sql.gz
```

Prueba local realizada durante la Fase 3:

1. Crear una base desechable (`db_saip_phase3_test`) vacía.
2. Aplicar migraciones hasta `898807c7b86f`, insertar NIT/teléfonos en claro.
3. `alembic upgrade head`: valores cifrados + `nit_hash` + `alembic check` limpio.
4. `alembic downgrade -1`: valores de nuevo en claro.
5. Eliminar la base desechable.

La misma base desechable sirve para probar el respaldo y la restauración antes
de cualquier cambio en un entorno real. No se ejecutó ninguna acción contra un
servidor de producción.

## Verificación local

```bash
cd backend
uv run ruff check .
uv run mypy
uv run alembic upgrade head
uv run alembic check
uv run pytest
docker compose config -q
docker compose -f docker-compose.prod.yml config -q
```

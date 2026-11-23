#!/usr/bin/env bash
# Respaldo lógico de MySQL con retención. Sin secretos en el código: usa las
# variables de entorno DB_* (o MYSQL_ROOT_PASSWORD dentro del contenedor db).
set -euo pipefail

DB_NAME="${DB_NAME:-db_saip_proyect}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-${MYSQL_ROOT_PASSWORD:-}}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"

mkdir -p "$BACKUP_DIR"
output="$BACKUP_DIR/${DB_NAME}_$(date +%Y%m%d_%H%M%S).sql.gz"

mysqldump \
  --host="$DB_HOST" --port="$DB_PORT" --user="$DB_USER" \
  --password="$DB_PASSWORD" \
  --single-transaction --routines --triggers \
  "$DB_NAME" | gzip > "$output"

find "$BACKUP_DIR" -maxdepth 1 -name "${DB_NAME}_*.sql.gz" \
  -mtime "+${RETENTION_DAYS}" -delete

echo "$output"

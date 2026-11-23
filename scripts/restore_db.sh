#!/usr/bin/env bash
# Restauración local de un respaldo generado por backup_db.sh.
# Uso: TARGET_DB=db_saip_restore ./scripts/restore_db.sh backups/archivo.sql.gz
set -euo pipefail

BACKUP_FILE="${1:?Uso: restore_db.sh <archivo.sql.gz>}"
DB_NAME="${DB_NAME:-db_saip_proyect}"
TARGET_DB="${TARGET_DB:-$DB_NAME}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-${MYSQL_ROOT_PASSWORD:-}}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"

if [[ ! "$TARGET_DB" =~ ^[A-Za-z0-9_]+$ ]]; then
  echo "Nombre de base inválido" >&2
  exit 1
fi
if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "No existe el respaldo: $BACKUP_FILE" >&2
  exit 1
fi

mysql \
  --host="$DB_HOST" --port="$DB_PORT" --user="$DB_USER" \
  --password="$DB_PASSWORD" \
  -e "CREATE DATABASE IF NOT EXISTS \`$TARGET_DB\` CHARACTER SET utf8mb4"

gunzip -c "$BACKUP_FILE" | mysql \
  --host="$DB_HOST" --port="$DB_PORT" --user="$DB_USER" \
  --password="$DB_PASSWORD" \
  "$TARGET_DB"

echo "Restaurado $BACKUP_FILE en $TARGET_DB"

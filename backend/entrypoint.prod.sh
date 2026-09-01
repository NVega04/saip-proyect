#!/bin/sh
set -e
echo ">>> Aplicando migraciones..."
alembic upgrade head
echo ">>> Iniciando uvicorn..."
exec python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers "${UVICORN_WORKERS:-4}"

#!/bin/bash
# Cuando usar? Cuando alguien tenga un error en DB de "revision not found", escribir en la base del proyecto
# el siguiente comando ./reset_db.sh este, va a iniciar esta secuencia y permitir reiniciar la DB a la
# version actual de master

set -e

echo "Iniciando limpieza profunda de la base de datos..."

# Detener contenedores y borrar volúmenes (esto elimina los datos físicos)
docker compose down -v

# Levantar los servicios en segundo plano
docker compose up -d

echo "Esperando a que MySQL esté disponible..."
max_attempts=30
attempt=0
until docker compose exec -T db mysqladmin ping -h localhost --silent 2>/dev/null; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "ERROR: MySQL no estuvo disponible después de $max_attempts intentos."
        exit 1
    fi
    echo "  Intento $attempt/$max_attempts - esperando 2 segundos..."
    sleep 2
done
echo "MySQL está listo."

run_with_retry() {
    local cmd="$1"
    local max_attempts=10
    local delay=5
    for i in $(seq 1 $max_attempts); do
        if eval "$cmd"; then
            return 0
        fi
        if [ $i -lt $max_attempts ]; then
            echo "  Reintentando comando... ($i/$max_attempts)"
            sleep $delay
        fi
    done
    echo "ERROR: El comando falló después de $max_attempts intentos."
    return 1
}

echo "Ejecutando migraciones..."
run_with_retry "docker exec saip_backend uv run alembic upgrade head"

echo "Ejecutando seeder..."
run_with_retry "docker exec saip_backend uv run python seed_data.py"

echo "Base de datos reseteada y actualizada a la última versión de master."
# docker compose exec backend uv run python seed_data.py, comando para ejecutar los seeders (sembradores)
# cuando se reinice la DB este se encarga de dejar los 2 datos principales, para uso de la app

import os
import time
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
import bcrypt
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "db_saip_proyect")

DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DB_URL)


def wait_for_db(max_attempts=15, delay=3):
    for i in range(max_attempts):
        try:
            test_engine = create_engine(DB_URL)
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            test_engine.dispose()
            print("Conexión a la base de datos establecida.")
            return
        except Exception:
            if i == max_attempts - 1:
                raise
            print(
                f"  Intento {i + 1}/{max_attempts} - DB no lista, esperando {delay}s..."
            )
            time.sleep(delay)


def seed():
    wait_for_db()
    with engine.begin() as conn:
        roles = [
            {
                "id": 1,
                "token": str(uuid.uuid4()),
                "name": "Admin",
                "description": "Acceso total",
                "status": "active",
            },
            {
                "id": 2,
                "token": str(uuid.uuid4()),
                "name": "Vendedor",
                "description": "Gestión de ventas y productos",
                "status": "active",
            },
        ]

        for role in roles:
            conn.execute(
                text("""
                INSERT IGNORE INTO roles (id, token, name, description, status, created_at, updated_at)
                VALUES (:id, :token, :name, :description, :status, NOW(), NOW())
                """),
                role,
            )

        admin_user = {
            "token": str(uuid.uuid4()),
            "first_name": "Admin",
            "last_name": "Sistema",
            "email": "admin@saip.com",
            "phone": "0000000000",
            "password_hash": bcrypt.hashpw(
                "admin123".encode(), bcrypt.gensalt()
            ).decode(),
            "status": "active",
            "is_admin": True,
            "role_id": 1,
        }

        conn.execute(
            text("""
            INSERT IGNORE INTO users (token, first_name, last_name, email, phone, password_hash, status, is_admin, role_id, created_at, updated_at)
            VALUES (:token, :first_name, :last_name, :email, :phone, :password_hash, :status, :is_admin, :role_id, NOW(), NOW())
            """),
            admin_user,
        )

    print("Seeding completado con éxito.")


if __name__ == "__main__":
    seed()

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

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

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

        modules = [
            {"id": 1, "token": str(uuid.uuid4()), "name": "dashboard", "label": "PANEL PRINCIPAL"},
            {"id": 2, "token": str(uuid.uuid4()), "name": "users", "label": "USUARIOS"},
            {"id": 3, "token": str(uuid.uuid4()), "name": "roles", "label": "ROLES"},
            {"id": 4, "token": str(uuid.uuid4()), "name": "inventory", "label": "INVENTARIO"},
            {"id": 5, "token": str(uuid.uuid4()), "name": "supplies", "label": "INSUMOS"},
            {"id": 6, "token": str(uuid.uuid4()), "name": "products", "label": "PRODUCTOS"},
            {"id": 7, "token": str(uuid.uuid4()), "name": "recipes", "label": "RECETAS"},
            {"id": 8, "token": str(uuid.uuid4()), "name": "production", "label": "PRODUCCIÓN"},
            {"id": 9, "token": str(uuid.uuid4()), "name": "providers", "label": "PROVEEDORES"},
            {"id": 10, "token": str(uuid.uuid4()), "name": "purchases", "label": "COMPRAS"},
            {"id": 11, "token": str(uuid.uuid4()), "name": "sales", "label": "VENTAS"},
            {"id": 12, "token": str(uuid.uuid4()), "name": "cash", "label": "CAJA"},
            {"id": 13, "token": str(uuid.uuid4()), "name": "reports", "label": "REPORTES"},
            {"id": 14, "token": str(uuid.uuid4()), "name": "quality", "label": "CONTROL DE CALIDAD"},
            {"id": 15, "token": str(uuid.uuid4()), "name": "delivery", "label": "DOMICILIOS"},
            {"id": 16, "token": str(uuid.uuid4()), "name": "menu", "label": "MENÚ / CARTA"},
            {"id": 17, "token": str(uuid.uuid4()), "name": "notifications", "label": "NOTIFICACIONES"},
            {"id": 18, "token": str(uuid.uuid4()), "name": "audit", "label": "AUDITORÍA"},
            {"id": 19, "token": str(uuid.uuid4()), "name": "settings", "label": "CONFIGURACIÓN"},
            {"id": 20, "token": str(uuid.uuid4()), "name": "support", "label": "SOPORTE"},
        ]
        for module in modules:
            conn.execute(
                text("""
                INSERT IGNORE INTO modules (id, token, name, label)
                VALUES (:id, :token, :name, :label)
                """),
                module,
            )

        conn.execute(text("DELETE FROM role_modules"))
        role_modules = []
        for module_id in range(1, 21):
            role_modules.append(
                {"role_id": 1, "module_id": module_id, "token": str(uuid.uuid4())}
            )
        role_modules.append(
            {"role_id": 2, "module_id": 11, "token": str(uuid.uuid4())}
        )
        for rm in role_modules:
            conn.execute(
                text("""
                INSERT IGNORE INTO role_modules (role_id, module_id, token)
                VALUES (:role_id, :module_id, :token)
                """),
                rm,
            )

    print("Seeding completado con éxito.")


if __name__ == "__main__":
    seed()

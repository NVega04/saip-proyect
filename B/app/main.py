from fastapi import FastAPI, Depends
from sqlmodel import Session, select
# Importamos la conexión y la función para crear tablas desde tu database.py
from .database import engine, create_db_and_tables, get_session

app = FastAPI(title="SAIP - Sistema de Panadería")

# --- ESTE ES EL BLOQUE QUE BUSCAMOS ---
@app.on_event("startup")
def on_startup():
    """
    Este código se ejecuta justo cuando inicias uvicorn.
    Se encarga de crear las tablas en MySQL si no existen.
    """
    print("Iniciando conexión con la base de datos...")
    create_db_and_tables()
    print("¡Tablas creadas/verificadas exitosamente!")
# --------------------------------------

@app.get("/")
def zz():
    return {"message": "Bienvenido al Backend de SAIP"}
# Aquí irán tus rutas del CRUD (POST, GET, etc.)
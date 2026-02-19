from fastapi import FastAPI
from sqlalchemy import create_engine

app = FastAPI()

# AQUÍ VA LA URL DE CONEXIÓN
# Formato: mysql+pymysql://USUARIO:CONTRASEÑA@HOST:PUERTO/NOMBRE_BD
DATABASE_URL = "mysql+pymysql://root:rootroot@host.docker.internal:3306/db_saip_proyect"

engine = create_engine(DATABASE_URL)

@app.get("/")
def read_root():
    return {"message": "Conectado al backend de SAIP"}
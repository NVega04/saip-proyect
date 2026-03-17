from fastapi import FastAPI
from src.routers import users
from src.routers import roles
from src.routers import session
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    # "https://saip.tudominio.com", ← CUANDO SE CARGUE A PRODUCCION
]

app = FastAPI(title="SAIP - Sistema administrativo integral de productos", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS, #Acceso desde el fronted al API
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "session-token"],
)


app.include_router(users.router)
app.include_router(roles.router)
app.include_router(session.router)
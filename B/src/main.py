from fastapi import FastAPI
from src.routers import users
from src.routers import roles
app = FastAPI(title="SAIP - Sistema administrativo integral de productos", version="1.0.0")
app.include_router(users.router)
app.include_router(roles.router)
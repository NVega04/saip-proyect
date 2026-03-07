from fastapi import FastAPI
from src.routers import users

app = FastAPI(title="SAIP - Sistema administrativo integral de productos", version="1.0.0")
app.include_router(users.router)

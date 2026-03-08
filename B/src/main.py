from fastapi import FastAPI
from src.routers import users
from src.routers import roles
from src.routers import auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SAIP", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(roles.router)
app.include_router(auth.router)
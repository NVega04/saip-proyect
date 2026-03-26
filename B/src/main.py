from fastapi import FastAPI
from src.routers import users
from src.routers import roles
from src.routers import session
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src.routers import role_modules
from src.routers import units
from src.routers import products
from src.routers import reports
from src.routers import supply_categories

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="SAIP - Sistema administrativo integral de productos", version="1.0.0"
)

ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "session_token", "X-Confirm-Password"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(users.router)
app.include_router(roles.router)
app.include_router(session.router)
app.include_router(role_modules.router)
app.include_router(units.router)
app.include_router(products.router)
app.include_router(reports.router)
app.include_router(supply_categories.router)

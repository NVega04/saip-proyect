import logging
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
from src.routers import supplies
from src.routers import providers
from src.routers.product_categories import router as product_categories_router
from src.routers.commercial_products import router as commercial_products_router
from src.routers.recipes import router as recipes_router

logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="SAIP - Sistema administrativo integral de productos", version="1.0.0"
)

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:8081",
    "http://161.35.6.77:5173",
    "exp://*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "session-token", "X-Confirm-Password"],
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
app.include_router(supplies.router)
app.include_router(providers.router)
app.include_router(product_categories_router)
app.include_router(commercial_products_router)
app.include_router(recipes_router)

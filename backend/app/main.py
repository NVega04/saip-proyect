import logging
from fastapi import FastAPI
from app.routers import users
from app.routers import roles
from app.routers import session
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.routers import role_modules
from app.routers import units
from app.routers import products
from app.routers import reports
from app.routers import supply_categories
from app.routers import supplies
from app.routers import providers
from app.routers.product_categories import router as product_categories_router
from app.routers.commercial_products import router as commercial_products_router
from app.routers.recipes import router as recipes_router

logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="SAIP - Sistema administrativo integral de productos", version="1.0.0"
)

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:8081",
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

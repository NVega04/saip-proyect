import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.core.config import settings
from src.core.exceptions import DomainError
from src.modules.auth.router import router as auth_router
from src.modules.commercial_products.categories_router import (
    router as product_categories_router,
)
from src.modules.commercial_products.router import (
    router as commercial_products_router,
)
from src.modules.health.router import router as health_router
from src.modules.inventory.router import router as inventory_router
from src.modules.production.router import router as production_router
from src.modules.products.router import router as products_router
from src.modules.providers.router import router as providers_router
from src.modules.recipes.router import router as recipes_router
from src.modules.reports.router import router as reports_router
from src.modules.roles.role_modules_router import router as role_modules_router
from src.modules.roles.router import router as roles_router
from src.modules.sales.router import router as sales_router
from src.modules.stats.router import router as stats_router
from src.modules.supplies.categories_router import (
    router as supply_categories_router,
)
from src.modules.supplies.router import router as supplies_router
from src.modules.units.router import router as units_router
from src.modules.users.router import router as users_router

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="SAIP - Sistema administrativo integral de productos", version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "session-token", "X-Confirm-Password"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(DomainError)
async def domain_error_handler(request, exc: DomainError):
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail}
    )


app.include_router(health_router)
app.include_router(users_router)
app.include_router(roles_router)
app.include_router(auth_router)
app.include_router(role_modules_router)
app.include_router(units_router)
app.include_router(products_router)
app.include_router(reports_router)
app.include_router(supply_categories_router)
app.include_router(supplies_router)
app.include_router(providers_router)
app.include_router(product_categories_router)
app.include_router(commercial_products_router)
app.include_router(recipes_router)
app.include_router(production_router)
app.include_router(sales_router)
app.include_router(stats_router)
app.include_router(inventory_router)

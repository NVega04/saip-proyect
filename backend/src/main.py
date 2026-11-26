from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.core.config import settings
from src.core.exceptions import DomainError
from src.core.logging import setup_logging
from src.core.middleware import RequestIdMiddleware
from src.core.openapi import AUTH_ERRORS
from src.core.rate_limit import limiter
from src.modules.audit.router import router as audit_router
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

setup_logging(settings.log_level, settings.log_format)

app = FastAPI(
    title="SAIP - Sistema administrativo integral de productos", version="1.0.0"
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORSMiddleware va último para que sea el más externo: así sus cabeceras
# aparecen también en los errores (incluido el 429) y no se enmascaran
# como errores CORS en el navegador.
app.add_middleware(RequestIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "session-token", "X-Confirm-Password"],
)


@app.exception_handler(DomainError)
async def domain_error_handler(request, exc: DomainError):
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail}
    )


# ``/health`` y ``/session`` (login/recuperación) son públicos; el resto
# comparte la documentación del error 401. Las respuestas declaradas en cada
# ruta prevalecen sobre estas (p. ej. 403/404/409 propios de cada operación).
app.include_router(health_router)
app.include_router(audit_router, responses=AUTH_ERRORS)
app.include_router(users_router, responses=AUTH_ERRORS)
app.include_router(roles_router, responses=AUTH_ERRORS)
app.include_router(auth_router)
app.include_router(role_modules_router, responses=AUTH_ERRORS)
app.include_router(units_router, responses=AUTH_ERRORS)
app.include_router(products_router, responses=AUTH_ERRORS)
app.include_router(reports_router, responses=AUTH_ERRORS)
app.include_router(supply_categories_router, responses=AUTH_ERRORS)
app.include_router(supplies_router, responses=AUTH_ERRORS)
app.include_router(providers_router, responses=AUTH_ERRORS)
app.include_router(product_categories_router, responses=AUTH_ERRORS)
app.include_router(commercial_products_router, responses=AUTH_ERRORS)
app.include_router(recipes_router, responses=AUTH_ERRORS)
app.include_router(production_router, responses=AUTH_ERRORS)
app.include_router(sales_router, responses=AUTH_ERRORS)
app.include_router(stats_router, responses=AUTH_ERRORS)
app.include_router(inventory_router, responses=AUTH_ERRORS)

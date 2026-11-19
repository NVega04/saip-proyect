# Inventario de la API SAIP

> Documento de referencia de la superficie HTTP, los modelos, los schemas y
> las reglas de acceso del backend. Se generó a partir de la aplicación real
> (`app.routes`, `SQLModel.metadata` y `app.openapi()`), no de una lista
> mantenida a mano. La suite de pruebas lo usa como respaldo: la matriz de
> rutas (`tests/smoke/route_matrix.py`) y el snapshot OpenAPI fallan si la
> aplicación se aparta de lo aquí descrito.

## 1. Metadatos

| Dato | Valor |
|---|---|
| Fecha de generación | 2026-11-17 |
| Rama | `fase-0-preparacion` (sobre `fase-1-arquitectura`) |
| Base del refactor | `0f86777` (`master`, previo a la Fase 1) |
| Versión de la app | 1.0.0 |
| Endpoints | 93 |
| Tablas | 21 |
| Schemas propios | 104 |
| Schemas usados directamente por operaciones | 63 |
| Título OpenAPI | SAIP - Sistema administrativo integral de productos |

Distribución por autenticación: **17 públicos**, **73 con sesión de
usuario**, **2 con módulo RBAC** (`inventory`) y **1 solo admin**.

## 2. Superficie HTTP (93 endpoints)

Leyenda de autenticación:

- **público**: no exige token.
- **usuario**: exige el header `session-token` con un JWT de una sesión activa.
- **admin**: además exige `User.is_admin = true`.
- **módulo `inventory`**: exige que el rol tenga asignado el módulo `inventory` (los admin lo saltan).

Código = código HTTP declarado por el endpoint. Las descargas y respuestas
`StreamingResponse` aparecen sin schema porque FastAPI no las describe.

### 2.1 Resumen por tag

| Tag | Endpoints | Públicos | Usuario | Admin | Módulo |
|---|---:|---:|---:|---:|---:|
| CommercialProducts | 7 | 1 | 6 | 0 | 0 |
| Health | 1 | 1 | 0 | 0 | 0 |
| Inventory | 3 | 1 | 0 | 0 | 2 |
| ProductCategories | 5 | 0 | 5 | 0 | 0 |
| Production | 9 | 1 | 8 | 0 | 0 |
| Products | 8 | 3 | 5 | 0 | 0 |
| Providers | 12 | 2 | 10 | 0 | 0 |
| Recipes | 5 | 0 | 5 | 0 | 0 |
| Reports | 1 | 0 | 1 | 0 | 0 |
| Role Modules | 3 | 0 | 2 | 1 | 0 |
| Roles | 4 | 1 | 3 | 0 | 0 |
| Sales | 5 | 0 | 5 | 0 | 0 |
| Session | 6 | 3 | 3 | 0 | 0 |
| Stats | 1 | 0 | 1 | 0 | 0 |
| Supplies | 7 | 1 | 6 | 0 | 0 |
| SupplyCategories | 5 | 0 | 5 | 0 | 0 |
| Units | 5 | 2 | 3 | 0 | 0 |
| Users | 6 | 1 | 5 | 0 | 0 |

### 2.2 Detalle

#### CommercialProducts (7)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/commercial-products/` | usuario | 200 | list[CommercialProductResponse] |  |
| POST | `/commercial-products/` | usuario | 201 | CommercialProductResponse |  |
| POST | `/commercial-products/bulk/import` | usuario | 200 | BulkImportResult |  |
| GET | `/commercial-products/bulk/template` | público | 200 | — | Plantilla Excel pública; OpenAPI la declara como `application/json`. |
| DELETE | `/commercial-products/{product_id}` | usuario | 200 | DeleteResponseCommercialProduct |  |
| GET | `/commercial-products/{product_id}` | usuario | 200 | CommercialProductResponse |  |
| PATCH | `/commercial-products/{product_id}` | usuario | 200 | CommercialProductResponse |  |

#### Health (1)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/health` | público | 200 | — | Consulta `SELECT 1` contra la BD. |

#### Inventory (3)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/inventory/bulk/template` | público | 200 | — | Plantilla Excel pública; OpenAPI la declara como `application/json`. |
| GET | `/inventory/report` | módulo `inventory` | 200 | — | Exige el módulo RBAC `inventory`. |
| GET | `/inventory/summary` | módulo `inventory` | 200 | InventoryPage | Exige el módulo RBAC `inventory`. |

#### ProductCategories (5)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/product-categories/` | usuario | 200 | list[ProductCategoryResponse] |  |
| POST | `/product-categories/` | usuario | 201 | ProductCategoryResponse |  |
| DELETE | `/product-categories/{category_id}` | usuario | 200 | DeleteResponseProductCategory |  |
| GET | `/product-categories/{category_id}` | usuario | 200 | ProductCategoryResponse |  |
| PUT | `/product-categories/{category_id}` | usuario | 200 | ProductCategoryResponse |  |

#### Production (9)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/production/orders/` | usuario | 200 | list[ProductionOrderResponse] |  |
| POST | `/production/orders/` | usuario | 201 | ProductionOrderResponse |  |
| POST | `/production/orders/bulk/import` | usuario | 200 | BulkImportResult |  |
| GET | `/production/orders/bulk/template` | público | 200 | — | Plantilla Excel pública; OpenAPI la declara como `application/json`. |
| GET | `/production/orders/export` | usuario | 200 | — | Descarga Excel; no declara schema en OpenAPI. |
| GET | `/production/orders/{order_id}` | usuario | 200 | ProductionOrderResponse |  |
| PATCH | `/production/orders/{order_id}/cancel` | usuario | 200 | ProductionOrderStatusChangeResponse |  |
| POST | `/production/orders/{order_id}/complete` | usuario | 200 | ProductionCompleteResponse |  |
| PATCH | `/production/orders/{order_id}/start` | usuario | 200 | ProductionOrderStatusChangeResponse |  |

#### Products (8)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/products/` | público | 200 | list[ProductResponse] | Público por decisión del código original. |
| POST | `/products/` | usuario | 201 | ProductResponse |  |
| POST | `/products/bulk/import` | usuario | 200 | BulkImportResult |  |
| GET | `/products/bulk/template` | público | 200 | — | Plantilla Excel pública; OpenAPI la declara como `application/json`. |
| DELETE | `/products/{product_id}` | usuario | 204 | — | Soft delete. Responde 204. |
| GET | `/products/{product_id}` | público | 200 | ProductResponse | Público por decisión del código original. |
| PATCH | `/products/{product_id}` | usuario | 200 | ProductResponse |  |
| PATCH | `/products/{product_id}/lock` | usuario | 200 | ProductResponse |  |

#### Providers (12)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/providers/` | usuario | 200 | list[ProviderResponse] |  |
| POST | `/providers/` | usuario | 201 | ProviderResponse |  |
| POST | `/providers/bulk/import` | usuario | 200 | BulkImportResult |  |
| GET | `/providers/bulk/template` | público | 200 | — | Plantilla Excel pública; OpenAPI la declara como `application/json`. |
| POST | `/providers/contacts/bulk/import` | usuario | 200 | BulkImportResult |  |
| GET | `/providers/contacts/bulk/template` | público | 200 | — | Plantilla Excel pública; OpenAPI la declara como `application/json`. |
| DELETE | `/providers/{provider_id}` | usuario | 200 | ProviderDeleteResponse |  |
| GET | `/providers/{provider_id}` | usuario | 200 | ProviderResponse |  |
| PATCH | `/providers/{provider_id}` | usuario | 200 | ProviderResponse |  |
| POST | `/providers/{provider_id}/contacts/` | usuario | 201 | ProviderContactResponse |  |
| DELETE | `/providers/{provider_id}/contacts/{contact_id}` | usuario | 200 | ProviderDeleteResponse |  |
| PATCH | `/providers/{provider_id}/contacts/{contact_id}` | usuario | 200 | ProviderContactResponse |  |

#### Recipes (5)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/recipes/` | usuario | 200 | list[RecipeResponse] |  |
| POST | `/recipes/` | usuario | 201 | RecipeResponse |  |
| DELETE | `/recipes/{recipe_id}` | usuario | 200 | DeleteResponseRecipe |  |
| GET | `/recipes/{recipe_id}` | usuario | 200 | RecipeResponse |  |
| PATCH | `/recipes/{recipe_id}` | usuario | 200 | RecipeResponse |  |

#### Reports (1)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/reports/{entity}` | usuario | 200 | — | Entidades válidas: 12 (ver sección 6). Formato `xlsx` o `json`. |

#### Role Modules (3)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/role-modules/modules` | usuario | 200 | list[ModuleResponse] |  |
| GET | `/role-modules/{role_id}` | usuario | 200 | list[RoleModuleResponse] |  |
| POST | `/role-modules/{role_id}` | admin | 200 | list[RoleModuleResponse] | Único endpoint con `require_admin`. |

#### Roles (4)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/roles/` | usuario | 200 | list[RolePublic] |  |
| POST | `/roles/` | público | 201 | RoleResponse | Público: crea roles sin autenticación (**riesgo**). |
| DELETE | `/roles/{role_id}` | usuario | 204 | — | Soft delete. Responde 204. |
| PATCH | `/roles/{role_id}` | usuario | 200 | RolePublic |  |

#### Sales (5)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/sales/` | usuario | 200 | SaleListPage |  |
| POST | `/sales/` | usuario | 201 | SaleCreateResponse |  |
| GET | `/sales/export` | usuario | 200 | — | Descarga Excel; no declara schema en OpenAPI. |
| GET | `/sales/{sale_id}` | usuario | 200 | SaleResponse |  |
| PATCH | `/sales/{sale_id}/annul` | usuario | 200 | SaleAnnulResponse |  |

#### Session (6)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| POST | `/session/change-password` | usuario | 200 | — |  |
| POST | `/session/forgot-password` | público | 200 | — |  |
| POST | `/session/login` | público | 200 | LoginResponse | Rate limit `5/minute`. Desactiva las sesiones activas anteriores del usuario. |
| POST | `/session/logout` | usuario | 200 | — | Usa el header `session_token` (guion bajo), no `session-token`. |
| POST | `/session/logout-all` | usuario | 200 | — |  |
| POST | `/session/reset-password` | público | 200 | — |  |

#### Stats (1)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/stats/dashboard` | usuario | 200 | DashboardStatsResponse |  |

#### Supplies (7)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/supplies/` | usuario | 200 | list[SupplyResponse] |  |
| POST | `/supplies/` | usuario | 201 | SupplyResponse |  |
| POST | `/supplies/bulk/import` | usuario | 200 | BulkImportResult |  |
| GET | `/supplies/bulk/template` | público | 200 | — | Plantilla Excel pública; OpenAPI la declara como `application/json`. |
| DELETE | `/supplies/{supply_id}` | usuario | 200 | DeleteResponseSupply |  |
| GET | `/supplies/{supply_id}` | usuario | 200 | SupplyResponse |  |
| PUT | `/supplies/{supply_id}` | usuario | 200 | SupplyResponse |  |

#### SupplyCategories (5)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/supply-categories/` | usuario | 200 | list[SupplyCategoryResponse] |  |
| POST | `/supply-categories/` | usuario | 201 | SupplyCategoryResponse |  |
| DELETE | `/supply-categories/{category_id}` | usuario | 200 | DeleteResponseSupplyCategory |  |
| GET | `/supply-categories/{category_id}` | usuario | 200 | SupplyCategoryResponse |  |
| PUT | `/supply-categories/{category_id}` | usuario | 200 | SupplyCategoryResponse |  |

#### Units (5)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/units/` | público | 200 | list[UnitResponse] | Público por decisión del código original. |
| POST | `/units/` | usuario | 201 | UnitResponse |  |
| DELETE | `/units/{unit_id}` | usuario | 204 | — | Soft delete. Responde 204. |
| GET | `/units/{unit_id}` | público | 200 | UnitResponse | Público por decisión del código original. |
| PATCH | `/units/{unit_id}` | usuario | 200 | UnitResponse |  |

#### Users (6)

| Método | Ruta | Auth | Código | Respuesta | Notas |
|---|---|---|---:|---|---|
| GET | `/users/` | usuario | 200 | list[UserResponse] |  |
| POST | `/users/` | público | 201 | UserResponse | Público: crea usuarios sin autenticación (**riesgo**). |
| DELETE | `/users/me` | usuario | 200 | DeleteResponseUser |  |
| GET | `/users/me` | usuario | 200 | UserResponse |  |
| DELETE | `/users/{user_id}` | usuario | 200 | DeleteResponseUser |  |
| PUT | `/users/{user_id}` | usuario | 200 | UserUpdateResponse |  |

## 3. Modelos de datos (21 tablas)

Todos los modelos viven en `src/modules/<dominio>/models.py` y se registran
en `SQLModel.metadata` desde `src/models_registry.py`.

| Módulo | Clase | Tabla | Columnas | PK | Soft delete | FKs |
|---|---|---|---:|---|---|---|
| `commercial_products` | `CommercialProduct` | `commercial_products` | 19 | id | sí | `product_categories.id`, `providers.id`, `units.id`, `users.id` |
| `commercial_products` | `ProductCategory` | `product_categories` | 11 | id | sí | `users.id` |
| `inventory` | `InventoryMovement` | `inventory_movements` | 12 | id | no | `users.id` |
| `production` | `ProductionOrder` | `production_orders` | 17 | id | sí | `recipes.id`, `users.id` |
| `production` | `ProductionOrderSnapshot` | `production_order_snapshots` | 8 | id | no | `production_orders.id`, `supplies.id`, `units.id` |
| `products` | `Product` | `products` | 16 | id | sí | `units.id`, `users.id` |
| `providers` | `Provider` | `providers` | 12 | id | sí | `users.id` |
| `providers` | `ProviderContact` | `provider_contacts` | 13 | id | sí | `providers.id`, `users.id` |
| `recipes` | `Recipe` | `recipes` | 14 | id | sí | `products.id`, `units.id`, `users.id` |
| `recipes` | `RecipeIngredient` | `recipe_ingredients` | 7 | id | no | `recipes.id`, `supplies.id`, `units.id` |
| `roles` | `Module` | `modules` | 4 | id | no | — |
| `roles` | `Role` | `roles` | 10 | id | sí | `users.id` |
| `roles` | `RoleModule` | `role_modules` | 4 | id | no | `modules.id`, `roles.id` |
| `sales` | `Sale` | `sales` | 12 | id | sí | `users.id` |
| `sales` | `SaleItem` | `sale_items` | 8 | id | no | `sales.id` |
| `supplies` | `Supply` | `supplies` | 18 | id | sí | `supply_categories.id`, `units.id`, `users.id` |
| `supplies` | `SupplyCategory` | `supply_categories` | 11 | id | sí | `users.id` |
| `units` | `Unit` | `units` | 12 | id | sí | `users.id` |
| `users` | `PasswordReset` | `password_resets` | 6 | id | no | `users.id` |
| `users` | `SessionApp` | `sessions` | 6 | id | no | `users.id` |
| `users` | `User` | `users` | 19 | id | sí | `roles.id`, `users.id` |

Notas de modelado:

- **Soft delete**: 13 de las 21 tablas tienen `deleted_at` y `deleted_by`. Las 8 restantes son de unión o de historial: `sessions`, `password_resets`, `role_modules`, `modules`, `recipe_ingredients`, `sale_items`, `inventory_movements` y `production_order_snapshots`.
- **Ciclo de FKs** entre `users.role_id → roles.id` y `roles.updated_by/deleted_by → users.id`: por eso el esquema se crea con `SET FOREIGN_KEY_CHECKS=0` en las pruebas y en Alembic se usan FKs diferidas (`use_alter=True`).
- **Tokens públicos**: casi todas las tablas de negocio exponen `token` UUID además del `id` autoincremental; la API sigue usando `id` en las rutas.

## 4. Schemas por módulo

| Módulo | Schemas | Nombres |
|---|---:|---|
| `auth` | 5 | `LoginRequest`, `LoginResponse`, `ForgotPasswordRequest`, `ResetPasswordRequest`, `ChangePasswordRequest` |
| `commercial_products` | 11 | `ProductCategoryBasic`, `CommercialProductBasic`, `ProductCategoryCreate`, `ProductCategoryUpdate`, `ProductCategoryResponse`, `DeleteResponseProductCategory`, `ProviderBasic`, `CommercialProductCreate`, `CommercialProductUpdate`, `CommercialProductResponse`, `DeleteResponseCommercialProduct` |
| `health` | 0 | — |
| `inventory` | 4 | `InventoryItemStatus`, `InventoryItem`, `InventorySummary`, `InventoryPage` |
| `production` | 7 | `RecipeBasic`, `ProductionOrderCreate`, `ProductionOrderCancelRequest`, `ProductionOrderResponse`, `ProductionOrderStatusChangeResponse`, `ProductionSnapshotResponse`, `ProductionCompleteResponse` |
| `products` | 3 | `ProductCreate`, `ProductUpdate`, `ProductResponse` |
| `providers` | 7 | `ProviderContactCreate`, `ProviderContactUpdate`, `ProviderContactResponse`, `ProviderCreate`, `ProviderUpdate`, `ProviderResponse`, `ProviderDeleteResponse` |
| `recipes` | 6 | `RecipeIngredientCreate`, `RecipeIngredientResponse`, `RecipeCreate`, `RecipeUpdate`, `RecipeResponse`, `DeleteResponseRecipe` |
| `reports` | 0 | — |
| `roles` | 7 | `RoleCreate`, `RoleResponse`, `RoleUpdate`, `RolePublic`, `ModuleResponse`, `RoleModuleAssign`, `RoleModuleResponse` |
| `sales` | 10 | `UserBasic`, `SaleItemCreate`, `SaleCreate`, `SaleItemResponse`, `SaleResponse`, `SaleListResponse`, `StockWarning`, `SaleListPage`, `SaleCreateResponse`, `SaleAnnulResponse` |
| `stats` | 22 | `DashboardKpis`, `ConsumptionPoint`, `StockLevelPoint`, `LowStockSupplyItem`, `ExpiringSupplyItem`, `SalesKpis`, `DailySalesPoint`, `TopSaleItem`, `ProductionByStatusPoint`, `DailyProductionPoint`, `TopRecipePoint`, `SalesSection`, `ProductionSection`, `ProductsKpis`, `ProductStockPoint`, `LowStockProduct`, `ProductProductionPoint`, `CommercialStockPoint`, `CategoryCountPoint`, `StockHealthPoint`, `ProductsSection`, `DashboardStatsResponse` |
| `supplies` | 10 | `SupplyBasic`, `SupplyCategoryBasic`, `SupplyCategoryCreate`, `SupplyCategoryUpdate`, `SupplyCategoryResponse`, `DeleteResponseSupplyCategory`, `SupplyCreate`, `SupplyUpdate`, `SupplyResponse`, `DeleteResponseSupply` |
| `units` | 4 | `UnitCreate`, `UnitUpdate`, `UnitResponse`, `UnitBasic` |
| `users` | 6 | `RoleBasic`, `UserCreate`, `UserResponse`, `DeleteResponseUser`, `UserUpdate`, `UserUpdateResponse` |
| `core` | 2 | `BulkRowError`, `BulkImportResult` |

Total: **104 schemas** definidos a mano (los `HTTPValidationError` y demás schemas automáticos de FastAPI no se cuentan).

Schemas usados directamente por más endpoints (los 12 primeros; los schemas anidados dentro de otro schema no cuentan aquí):

| Schema | Endpoints que lo usan |
|---|---:|
| `BulkImportResult` | 6 |
| `ProductResponse` | 5 |
| `CommercialProductResponse` | 4 |
| `ProductCategoryResponse` | 4 |
| `ProviderResponse` | 4 |
| `RecipeResponse` | 4 |
| `SupplyCategoryResponse` | 4 |
| `SupplyResponse` | 4 |
| `UnitResponse` | 4 |
| `ProductionOrderResponse` | 3 |
| `UserResponse` | 3 |
| `DeleteResponseUser` | 2 |

## 5. Dependencias compartidas y headers

| Dependencia | Archivo | Comportamiento |
|---|---|---|
| `get_session` | `src/core/database.py` | Abre una `Session` con el engine de desarrollo. En pruebas se reemplaza con `app.dependency_overrides`. |
| `get_current_user` | `src/core/dependencies.py` | Lee el header `session-token`, decodifica el JWT y valida la fila de `sessions` (existencia, `is_active` y `expires_at`). Devuelve el `User`. |
| `require_module(name)` | `src/core/dependencies.py` | Si el usuario no es admin, busca `role_modules` del rol. Sin acceso → 403. |
| `require_admin` | `src/core/dependencies.py` | Exige `is_admin`; si no → 403. |
| `DomainError` handler | `src/main.py` | Traduce excepciones de dominio a `{"detail": ...}` con el código definido en la excepción. |

### 5.1 Headers

| Header | Alias en código | Uso |
|---|---|---|
| `session-token` | `session-token` | Autenticación de todos los endpoints protegidos. Es el único header de sesión incluido en `allow_headers` de CORS. |
| `session_token` | `session_token` | Solo `POST /session/logout`. **No** está en `allow_headers` de CORS: un navegador no puede enviarlo en un preflight. |
| `X-Confirm-Password` | `X-Confirm-Password` | Solo `DELETE /users/me`: confirma la contraseña antes de la baja lógica. |

### 5.2 CORS (Fase 2)

Los orígenes ya no están hardcodeados: se leen de `CORS_ORIGINS` (CSV) en
`src.core.config`. La configuración de referencia es
`http://localhost:5173,https://saip.lat`. Se normalizan quitando espacios y
barras finales, se deduplican y se rechazan comodines o esquemas distintos de
`http://`/`https://`.

`allow_methods` = `GET, POST, PUT, PATCH, DELETE, OPTIONS`;
`allow_headers` = `Content-Type, session-token, X-Confirm-Password`;
`allow_credentials = true`.

Preflight verificado contra la app real:

| Origen | Resultado |
|---|---|
| `http://localhost:5173` | 200, ACAO reflejado |
| `https://saip.lat` | 200, ACAO reflejado |
| `https://saip.lat/` | 400 (barra final rechazada) |
| `exp://*` | 400 |
| `http://161.35.6.77:5173` | 400 |

### 5.3 Códigos de error

| Excepción | HTTP |
|---|---:|
| `NotFoundError` | 404 |
| `ConflictError` | 409 |
| `BusinessRuleError` | 400 |
| `UnauthorizedError` | 401 |
| `PermissionDeniedError` | 403 |
| `LockedError` | 423 |
| `GoneError` | 410 |
| `UnprocessableError` | 422 |
| `ServerError` | 500 |

**Importante**: si falta el header `session-token`, FastAPI responde **422** (error de validación), no 401. El 401 aparece cuando el header existe pero el token es inválido o la sesión está vencida/inactiva. La suite fija este contrato en `tests/smoke/test_unauthorized.py`.

## 6. Quirks y riesgos conocidos

Se documentan tal como están; **ninguno se corrige en la Fase 0** para no
cambiar comportamiento.

### 6.1 Endpoints públicos (17)

| Método | Ruta | Motivo |
|---|---|---|
| GET | `/commercial-products/bulk/template` | Plantilla Excel descargable. |
| GET | `/health` | Healthcheck para Docker y monitoreo. |
| GET | `/inventory/bulk/template` | Plantilla Excel descargable. |
| GET | `/production/orders/bulk/template` | Plantilla Excel descargable. |
| GET | `/products/` | Catálogo de solo lectura, público por decisión previa. |
| GET | `/products/bulk/template` | Plantilla Excel descargable. |
| GET | `/products/{product_id}` | Catálogo de solo lectura, público por decisión previa. |
| GET | `/providers/bulk/template` | Plantilla Excel descargable. |
| GET | `/providers/contacts/bulk/template` | Plantilla Excel descargable. |
| POST | `/roles/` | **Creación de roles sin autenticación** (riesgo de seguridad). |
| POST | `/session/forgot-password` | Solicitud de recuperación. |
| POST | `/session/login` | Inicio de sesión. |
| POST | `/session/reset-password` | Canje del token de recuperación. |
| GET | `/supplies/bulk/template` | Plantilla Excel descargable. |
| GET | `/units/` | Catálogo de solo lectura, público por decisión previa. |
| GET | `/units/{unit_id}` | Catálogo de solo lectura, público por decisión previa. |
| POST | `/users/` | **Creación de usuarios sin autenticación** (riesgo de seguridad). |

**Riesgo principal**: `POST /users/` y `POST /roles/` permiten crear cuentas
y roles sin token. Es el hallazgo más relevante para las fases de seguridad.

Otros comportamientos a tener en cuenta:

- **Solo un endpoint admin**: `POST /role-modules/{role_id}`. El resto de la API solo valida sesión (o el módulo `inventory`).
- **RBAC mínimo**: únicamente `inventory/report` e `inventory/summary` consultan `role_modules`. Los demás módulos no aplican RBAC hoy.
- **Ventas**: `item_type` acepta `product` y `commercial`; `supply` existe en el enum pero el servicio no lo resuelve y termina en 404. Stock insuficiente → 409.
- **Mayúsculas**: `UppercaseMixin` aplica `upper()` a la mayoría de strings de entrada; excluye `email`, `description`, `password`, `token`, `new_password`, `current_password`, `notas`, `observaciones` y `status`.
- **Borrados**: `DELETE /products/{id}`, `/units/{id}` y `/roles/{id}` responden 204; los demás borrados son soft delete y responden 200 con un schema `DeleteResponse*`.
- **Login**: `POST /session/login` tiene rate limit `5/minute` y desactiva las demás sesiones activas del usuario. Un login fallido incrementa el contador; a los 3 intentos la cuenta se bloquea temporalmente (423).
- **Reportes**: `GET /reports/{entity}` soporta 12 entidades (`users`, `roles`, `sessions`, `products`, `supplies`, `supply-categories`, `units`, `recipes`, `production`, `providers`, `product-categories`, `commercial-products`). Entidad desconocida → 404.
- **OpenAPI incompleto en descargas**: las plantillas y exportaciones Excel no declaran su `media_type` real; OpenAPI las muestra como `application/json` o sin schema.
- **Logout**: el alias `session_token` (guion bajo) difiere del resto y no está permitido por CORS, por lo que el navegador lo bloquea en peticiones cross-origin.
- **Pydantic v2**: los schemas usan `class Config` (deprecado). Genera advertencias; es deuda preexistente.

## 7. Contrato OpenAPI y snapshot

El contrato se congela en `backend/tests/snapshots/openapi_baseline.json`:

| Dato | Valor |
|---|---|
| Origen | `app.openapi()` del commit `0f86777` (`master`, antes de la Fase 1) |
| Paths | 59 |
| Schemas | 120 |
| SHA-256 | `3f2bc1bef68fca4138e88d4abd996c7fafbd02958e1f08f948a6eeb3f1295902` |
| Test | `backend/tests/test_openapi_snapshot.py` |

El test compara paths, métodos, parámetros, request bodies, respuestas y
schemas; ignora solo `servers` (volátil según el host). Un cambio de
contrato obliga a actualizar el snapshot con aprobación explícita. Ver
`backend/tests/snapshots/README.md`.

## 8. Deriva de Alembic (corregida)

Se comparó una base creada solo con `alembic upgrade head` contra
`SQLModel.metadata`. Resultado inicial: **21 tablas + `alembic_version` = 22**,
sin tablas faltantes, pero con **6 foreign keys presentes en los modelos y
ausentes en las migraciones**:

| Tabla | Columna | Referencia |
|---|---|---|
| `commercial_products` | `deleted_by` | `users.id` |
| `commercial_products` | `updated_by` | `users.id` |
| `product_categories` | `deleted_by` | `users.id` |
| `product_categories` | `updated_by` | `users.id` |
| `sales` | `deleted_by` | `users.id` |
| `sales` | `updated_by` | `users.id` |

La deriva se cerró en la rama `fase-1-cierre-alembic` con la revisión
`756185c644ac` (hija de `cd4e9f97101f`). Antes de escribirla se verificó que
las 6 columnas no tenían filas huérfanas. La migración usa `use_alter=True` y
no modifica revisiones ya aplicadas.

Validación realizada en una base desechable: `upgrade head` dejó 0 FKs
faltantes y 0 sobrantes frente a la metadata, `alembic check` terminó con
`No new upgrade operations detected.`, y el ciclo
`downgrade -1 → upgrade head` eliminó y restauró exactamente las 6
restricciones. La misma revisión se aplicó a la base de desarrollo y la suite
completa sigue en verde (227 tests).

## 9. Regla de mantenimiento

Cuando se agregue, elimine o cambie un endpoint, un modelo o un schema:

1. Actualizar `backend/tests/smoke/route_matrix.py` con la nueva ruta y su
   clasificación de auth. El test `test_route_coverage.py` falla si la
   matriz y `app.routes` no coinciden.
2. Actualizar este inventario: tabla de endpoints, modelos o schemas según
   corresponda, y la fecha de generación.
3. Si cambió el contrato, actualizar el snapshot OpenAPI **solo con
   aprobación explícita** y documentar el motivo en el commit.
4. Ejecutar toda la suite:

```bash
docker compose run --rm backend uv run pytest -q
```

5. En CI, la misma orden debe pasar antes de mergear.

La fuente de verdad siempre es el código; este documento se regenera a
partir de `app.routes`, `SQLModel.metadata` y `app.openapi()`.

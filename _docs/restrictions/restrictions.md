## Restricciones

### 1. Unicidad

| Entidad | Campo | Detalle |
|---------|-------|---------|
| Usuarios | `email` | No pueden existir dos usuarios con el mismo correo electrónico |
| Usuarios | `token` | Token UUID único por usuario |
| Roles | `token` | Token UUID único por rol |
| Módulos | `name` | El identificador del módulo debe ser único (ej: "inventory", "sales") |
| Unidades | `token` | Token UUID único por unidad |
| Productos | `token` | Token UUID único por producto |
| Categorías de insumos | `name` | No pueden existir dos categorías de insumos con el mismo nombre |
| Insumos | `name` | No pueden existir dos insumos con el mismo nombre |
| Insumos | `token` | Token UUID único por insumo |
| Recetas | `token` | Token UUID único por receta |
| Ingredientes de receta | `token` | Token UUID único por ingrediente |
| Órdenes de producción | `token` | Token UUID único por orden |
| Snapshots de producción | `token` | Token UUID único por snapshot |
| Categorías de productos | `name` | No pueden existir dos categorías de productos con el mismo nombre |
| Productos comerciales | `token` | Token UUID único por producto comercial |
| Proveedores | `nit` | No pueden existir dos proveedores con el mismo NIT |
| Proveedores | `email` | No pueden existir dos proveedores con el mismo correo |
| Proveedores | `token` | Token UUID único por proveedor |
| Contactos de proveedor | `token` | Token UUID único por contacto |
| Sesiones | `token` | Token UUID único por sesión |
| Restablecimientos de contraseña | `token` | Token único por solicitud |

### 2. Longitud máxima de campos

| Entidad | Campo | Máximo |
|---------|-------|--------|
| Usuarios | `first_name` | 100 caracteres |
| Usuarios | `last_name` | 100 caracteres |
| Usuarios | `email` | 150 caracteres |
| Usuarios | `phone` | 20 caracteres |
| Usuarios | `password_hash` | 255 caracteres |
| Roles | `name` | 100 caracteres |
| Roles | `description` | 500 caracteres |
| Módulos | `name` | 100 caracteres |
| Módulos | `label` | 100 caracteres |
| Unidades | `name` | 100 caracteres |
| Unidades | `abbreviation` | 20 caracteres |
| Unidades | `description` | 255 caracteres |
| Productos | `name` | 150 caracteres |
| Productos | `description` | 500 caracteres |
| Categorías de insumos | `name` | 100 caracteres |
| Categorías de insumos | `description` | 255 caracteres |
| Insumos | `name` | 150 caracteres |
| Insumos | `description` | 500 caracteres |
| Recetas | `name` | 150 caracteres |
| Recetas | `description` | 500 caracteres |
| Ingredientes de receta | `notes` | 255 caracteres |
| Órdenes de producción | `notes` | 500 caracteres |
| Categorías de productos | `name` | 100 caracteres |
| Categorías de productos | `description` | 255 caracteres |
| Productos comerciales | `name` | 150 caracteres |
| Productos comerciales | `description` | 500 caracteres |
| Proveedores | `company` | 150 caracteres |
| Proveedores | `nit` | 20 caracteres |
| Proveedores | `email` | 150 caracteres |
| Contactos de proveedor | `name` | 150 caracteres |
| Contactos de proveedor | `email` | 150 caracteres |
| Contactos de proveedor | `phone` | 20 caracteres |
| Contactos de proveedor | `notes` | 500 caracteres |
| Restablecimientos de contraseña | `token` | 255 caracteres |

### 3. Llaves foráneas (relaciones obligatorias)

| Entidad | Campo | Referencia | ¿Nullable? |
|---------|-------|------------|------------|
| Usuarios | `role_id` | roles.id | No |
| Sesiones | `user_id` | users.id | No |
| Restablecimientos | `user_id` | users.id | No |
| RoleModule | `role_id` | roles.id | No |
| RoleModule | `module_id` | modules.id | No |
| Productos | `unit_id` | units.id | No |
| Insumos | `category_id` | supply_categories.id | No |
| Insumos | `unit_id` | units.id | No |
| Insumos | `supplier_id` | users.id | Sí |
| Recetas | `product_id` | products.id | Sí |
| Recetas | `yield_unit_id` | units.id | No |
| Ingredientes | `recipe_id` | recipes.id | No |
| Ingredientes | `supply_id` | supplies.id | No |
| Ingredientes | `unit_id` | units.id | No |
| Órdenes de producción | `recipe_id` | recipes.id | No |
| Snapshots | `production_order_id` | production_orders.id | No |
| Snapshots | `supply_id` | supplies.id | No |
| Snapshots | `unit_id` | units.id | No |
| Productos comerciales | `category_id` | product_categories.id | No |
| Productos comerciales | `unit_id` | units.id | No |
| Productos comerciales | `provider_id` | providers.id | Sí |
| Contactos de proveedor | `provider_id` | providers.id | No |

### 4. Soft delete (eliminación lógica)

Todas las entidades principales implementan borrado lógico, no físico:

| Entidad | Campos de soft delete |
|---------|----------------------|
| Usuarios | `deleted_at`, `deleted_by` |
| Roles | `deleted_at`, `deleted_by` |
| Unidades | `deleted_at`, `deleted_by` |
| Productos | `deleted_at`, `deleted_by` |
| Categorías de insumos | `deleted_at`, `deleted_by` |
| Insumos | `deleted_at`, `deleted_by` |
| Recetas | `deleted_at`, `deleted_by` |
| Órdenes de producción | `deleted_at`, `deleted_by` |
| Categorías de productos | `deleted_at`, `deleted_by` |
| Productos comerciales | `deleted_at`, `deleted_by` |
| Proveedores | `deleted_at`, `deleted_by` |
| Contactos de proveedor | `deleted_at`, `deleted_by` |

### 5. Auditoría

| Entidad | Campos de auditoría |
|---------|---------------------|
| Usuarios | `created_at`, `updated_at`, `updated_by`, `deleted_at`, `deleted_by` |
| Roles | `created_at`, `updated_at`, `updated_by`, `deleted_at`, `deleted_by` |
| Unidades | `created_at`, `created_by`, `updated_at`, `updated_by`, `deleted_at`, `deleted_by` |
| Productos | `created_at`, `created_by`, `updated_at`, `updated_by`, `deleted_at`, `deleted_by` |
| Categorías de insumos | `created_at`, `created_by`, `updated_at`, `updated_by`, `deleted_at`, `deleted_by` |
| Insumos | `created_at`, `created_by`, `updated_at`, `updated_by`, `deleted_at`, `deleted_by` |
| Recetas | `created_at`, `created_by`, `updated_at`, `updated_by`, `deleted_at`, `deleted_by` |
| Órdenes de producción | `created_at`, `created_by`, `updated_at`, `updated_by`, `deleted_at`, `deleted_by` |
| Categorías de productos | `created_at`, `created_by`, `updated_at`, `updated_by`, `deleted_at`, `deleted_by` |
| Productos comerciales | `created_at`, `created_by`, `updated_at`, `updated_by`, `deleted_at`, `deleted_by` |
| Proveedores | `created_at`, `created_by`, `updated_at`, `updated_by`, `deleted_at`, `deleted_by` |
| Contactos de proveedor | `created_at`, `created_by`, `updated_at`, `updated_by`, `deleted_at`, `deleted_by` |

### 6. Autenticación y seguridad

- **Sesión por token**: Cada sesión tiene un token UUID único almacenado en BD con fecha de expiración
- **JWT**: Se genera un JWT firmado con HS256 que contiene `user_id` y `session_token`
- **Duración de sesión**: 8 horas desde su creación
- **Hash de contraseña**: Se usa bcrypt con salt automático (`hash_password` / `verify_password`)
- **Contraseña temporal**: Formato `Temp@XXXXYY` (4 dígitos + 2 letras mayúsculas)
- **Rate limiting** (SlowAPI):
  - Login: máximo 5 solicitudes por minuto por IP
  - Recuperación de contraseña: máximo 3 solicitudes por minuto por IP
- **CORS**: Solo se permiten orígenes específicos (`localhost:5173`, `localhost:8081`, `exp://*`)
- **Métodos HTTP permitidos**: GET, POST, PUT, PATCH, DELETE, OPTIONS
- **Headers permitidos**: `Content-Type`, `session-token`, `X-Confirm-Password`
- **Baja de cuenta**: Requiere confirmación de contraseña actual (`X-Confirm-Password`)
- **Términos y condiciones**: El usuario debe aceptarlos al iniciar sesión (`accepted_terms`)

### 7. Conversión automática a mayúsculas (UppercaseMixin)

Todos los campos de tipo string en las solicitudes se convierten automáticamente a mayúsculas, **excepto**:

- `email`
- `description`
- `password`
- `token`
- `new_password`
- `current_password`
- `notas`
- `observaciones`
- `status`

### 8. Valores por defecto

| Entidad | Campo | Valor por defecto |
|---------|-------|-------------------|
| Usuarios | `status` | `"active"` |
| Usuarios | `is_admin` | `false` |
| Usuarios | `accepted_terms` | `false` |
| Roles | `status` | `"active"` |
| Sesiones | `is_active` | `true` |
| Restablecimientos | `used` | `false` |
| Productos | `available_quantity` | `0` |
| Productos | `min_stock` | `0` |
| Productos | `max_stock` | `0` |
| Productos | `is_locked` | `false` |
| Productos | `status` | `"active"` |
| Categorías de insumos | `status` | `"active"` |
| Insumos | `available_quantity` | `0` |
| Insumos | `min_stock` | `0` |
| Insumos | `max_stock` | `0` |
| Insumos | `status` | `"active"` |
| Recetas | `yield_quantity` | `1` |
| Recetas | `status` | `"active"` |
| Órdenes de producción | `quantity_multiplier` | `1` |
| Órdenes de producción | `total_yield` | `0` |
| Órdenes de producción | `status` | `"pending"` |
| Categorías de productos | `status` | `"active"` |
| Productos comerciales | `purchase_price` | `0` |
| Productos comerciales | `sale_price` | `0` |
| Productos comerciales | `available_quantity` | `0` |
| Productos comerciales | `min_stock` | `0` |
| Productos comerciales | `max_stock` | `0` |
| Productos comerciales | `status` | `"active"` |
| Proveedores | `status` | `"active"` |

### 9. Tipos enumerados (Enum)

| Enum | Valores |
|------|---------|
| `UserStatus` | `active`, `inactive` |
| `RoleStatus` | `active`, `inactive` |
| `ProductStatus` | `active`, `inactive` |
| `ProviderStatus` | `active`, `inactive` |
| `RecipeStatus` | `active`, `inactive` |
| `ProductionOrderStatus` | `pending`, `in_progress`, `completed`, `cancelled` |

### 10. Zona horaria

- Todas las marcas de tiempo se generan en la zona horaria `America/Bogota` (UTC-5)

### 11. Frontend

- **Token de sesión**: Se almacena en `localStorage` bajo la clave `session_token`
- **Módulos permitidos**: Se almacenan en `localStorage` bajo la clave `modules` (array JSON)
- **Alias de módulos**: `sales-history` se trata como `sales` para permisos
- **Módulos siempre accesibles**: `dashboard`, `acerca`, `contacto` (no requieren permiso explícito)
- **Rutas protegidas**: Cada ruta del frontend puede requerir un módulo específico mediante el componente `ProtectedRoute`
- **API Fetch**: Toda solicitud al backend incluye automáticamente el header `session-token` y `Content-Type: application/json`
- **Redirección por 401**: Si el backend responde 401, se limpia `localStorage` y se redirige a `/`

### 12. Correo electrónico (SMTP)

- **Correo de bienvenida**: Se envía al crear un usuario, incluye contraseña temporal
- **Correo de recuperación**: Se envía al solicitar restablecimiento de contraseña, incluye token
- **Correo de desactivación**: Se envía al desactivar una cuenta de usuario

### 13. Infraestructura

- **Base de datos**: MySQL 8.0 en contenedor Docker, puerto `3307` (host) → `3306` (contenedor)
- **Backend**: Puerto `8000`, expuesto por contenedor Docker
- **Frontend**: Puerto `5173`, expuesto por contenedor Docker (Vite dev server)
- **Red Docker**: Los tres servicios comparten la red `app`

### 14. Validaciones adicionales

- **Stock**: `available_quantity`, `min_stock` y `max_stock` deben ser valores numéricos (`float`), sin validación de negatividad explícita en el modelo (se valida en el frontend)
- **Bloqueo de productos**: Un producto puede estar bloqueado (`is_locked = true`), lo que impide ciertas operaciones (definido en el router correspondiente)
- **Protección de rol Admin**: El rol con id=1 (Admin) no puede ser eliminado
- **Relación Receta-Producto**: Una receta puede estar asociada opcionalmente a un producto (`product_id` nullable)
- **Multiplicador de producción**: `quantity_multiplier` mínimo 1 por defecto en órdenes de producción
- **Snapshot de producción**: Al completar una orden, se captura `stock_before` y `stock_after` de cada insumo utilizado

-- ============================================================
-- PROYECTO DE GRADO: SAIP - Sistema Administrativo Integral de Productos
-- EVIDENCIA: Script de Validación BD vs. Aplicación (Punto 3.4)
-- ALUMNO/GRUPO: [Nombre del equipo]
-- BASE DE DATOS REAL: db_saip_proyect (contenedor saip_db_container)
-- ESQUEMA: Generado por SQLModel (users, products, sales, providers, etc.)
--
-- EJECUCIÓN:
--   docker exec saip_db_container mysql -uroot -proot_password db_saip_proyect < 00_estado_inicial.sql
-- ============================================================
--
-- NOTA IMPORTANTE:
--   El archivo saip.sql del repositorio está DESACTUALIZADO. Usa nombres
--   obsoletos (usuarios, productos, ventas, movimientos_invetario). El
--   esquema REAL de la base está generado desde los modelos SQLModel del
--   backend. Todas las pruebas válidas se ejecutan contra el esquema real.
--
-- ============================================================
-- ESTADO INICIAL DE LA BASE DE DATOS (Paso 1 del Punto 3.4)
-- ============================================================

SELECT '=== 1. USUARIOS ===' AS 'ESTADO INICIAL';
SELECT id, email, first_name, last_name, status, is_admin, role_id
FROM users
WHERE deleted_at IS NULL
ORDER BY id;

SELECT '=== 2. ROLES ===' AS 'ESTADO INICIAL';
SELECT id, name, description, status
FROM roles
WHERE deleted_at IS NULL
ORDER BY id;

SELECT '=== 3. UNIDADES DE MEDIDA ===' AS 'ESTADO INICIAL';
SELECT id, name, abbreviation, quantity
FROM units
WHERE deleted_at IS NULL
ORDER BY id;

SELECT '=== 4. PROVEEDORES ===' AS 'ESTADO INICIAL';
SELECT id, company, nit, email, status
FROM providers
WHERE deleted_at IS NULL
ORDER BY id;

SELECT '=== 5. PRODUCTOS ===' AS 'ESTADO INICIAL';
SELECT id, name, unit_id, available_quantity, min_stock, max_stock, status
FROM products
WHERE deleted_at IS NULL
ORDER BY id;

SELECT '=== 6. CATEGORIAS DE INSUMOS ===' AS 'ESTADO INICIAL';
SELECT id, name, status FROM supply_categories ORDER BY id;

SELECT '=== 7. CATEGORIAS DE PRODUCTOS ===' AS 'ESTADO INICIAL';
SELECT id, name, status FROM product_categories ORDER BY id;

SELECT '=== 8. INSUMOS ===' AS 'ESTADO INICIAL';
SELECT id, name, category_id, unit_id, available_quantity, status
FROM supplies
WHERE deleted_at IS NULL
ORDER BY id;

SELECT '=== 9. PRODUCTOS COMERCIALES ===' AS 'ESTADO INICIAL';
SELECT id, name, category_id, unit_id, available_quantity, status
FROM commercial_products
WHERE deleted_at IS NULL
ORDER BY id;

SELECT '=== 10. RECETAS ===' AS 'ESTADO INICIAL';
SELECT id, name, product_id, yield_quantity, yield_unit_id, status
FROM recipes
WHERE deleted_at IS NULL
ORDER BY id;

SELECT '=== 11. VENTAS ===' AS 'ESTADO INICIAL';
SELECT id, user_id, sale_date, status, notes FROM sales WHERE deleted_at IS NULL ORDER BY id;

SELECT '=== 12. MOVIMIENTOS DE INVENTARIO ===' AS 'ESTADO INICIAL';
SELECT id, item_type, item_id, movement_type, quantity, stock_before, stock_after, reference_type, reference_id
FROM inventory_movements ORDER BY id;

-- Fin del estado inicial

-- ============================================================
-- PROYECTO DE GRADO: SAIP
-- EVIDENCIA 01: CASOS DE PRUEBA - OPERACIONES CREATE (INSERT)
-- Punto 3.4 - Paso 3 y 4
-- 11 endpoints CREATE x 2 funcionalidades = 22 casos
-- ============================================================
-- METODOLOGÍA POR CASO:
--   Funcionalidad POSITIVA : Insert válido -> SELECT verifica fila -> ROLLBACK (datos de prueba, no contaminan)
--   Funcionalidad NEGATIVA : Insert inválido (FK/UNIQUE/obligatorio) -> la BD lo rechaza -> SELECT certifica 0 filas
-- ============================================================

-- ════════════════════════════════════════════════════════════
-- CASO 1. POST /users/  (Crear usuario) - FK a roles.id
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 1: POST /users/ ===' AS 'PRUEBA';

-- 1.1 FUNCIONALIDAD POSITIVA: crear usuario con role_id válido (existe rol id=1)
START TRANSACTION;
INSERT INTO users (token, first_name, last_name, email, password_hash, role_id, status, is_admin, accepted_terms, created_at)
VALUES (UUID(), 'JUAN', 'PEREZ', 'qa.juan.perez@saip.com', 'hash_demo_prueba', 1, 'ACTIVE', 0, 1, NOW());
-- Verificación: fila insertada y relación FK correcta
SELECT '1.1 POSITIVO - usuario insertado:' AS 'VERIFICACION';
SELECT u.id, u.first_name, u.last_name, u.email, u.role_id, r.name AS rol, u.status
FROM users u
JOIN roles r ON r.id = u.role_id
WHERE u.email = 'qa.juan.perez@saip.com';
ROLLBACK;

-- 1.2 FUNCIONALIDAD NEGATIVA: crear usuario con role_id inexistente (viola FK)
START TRANSACTION;
-- ¡ERROR ESPERADO: fallará la FOREIGN KEY (role inexistente 9999)!
INSERT INTO users (token, first_name, last_name, email, password_hash, role_id, status, is_admin, accepted_terms, created_at)
VALUES (UUID(), 'MARIA', 'LOPEZ', 'qa.maria.lopez@saip.com', 'hash_demo', 9999, 'ACTIVE', 0, 1, NOW());
ROLLBACK;
SELECT '1.2 NEGATIVO - NO debe existir fila (FK inválida):' AS 'VERIFICACION';
SELECT COUNT(*) AS filas_con_fk_invalida FROM users WHERE role_id = 9999;

-- ════════════════════════════════════════════════════════════
-- CASO 2. POST /roles/  (Crear rol) - UNIQUE name
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 2: POST /roles/ ===' AS 'PRUEBA';

-- 2.1 FUNCIONALIDAD POSITIVA
START TRANSACTION;
INSERT INTO roles (token, name, description, status, created_at)
VALUES (UUID(), 'JEFE DE ALMACEN', 'ROLE DE PRUEBA QA', 'ACTIVE', NOW());
SELECT '2.1 POSITIVO - rol insertado:' AS 'VERIFICACION';
SELECT id, name, description, status FROM roles WHERE name = 'JEFE DE ALMACEN';
ROLLBACK;

-- 2.2 FUNCIONALIDAD NEGATIVA: viola UNIQUE name (rol 'Admin' ya existe, id=1)
START TRANSACTION;
-- ¡ERROR ESPERADO: retomará el nombre duplicado según consulte la app (409) o UNIQUE en BD!
INSERT INTO roles (token, name, description, status, created_at)
VALUES (UUID(), 'Admin', 'ROL DUPLICADO PRUEBA', 'ACTIVE', NOW());
ROLLBACK;
SELECT '2.2 NEGATIVO - solo debe existir 1 rol Admin (sin duplicado):' AS 'VERIFICACION';
SELECT name, COUNT(*) AS ocurrencias FROM roles WHERE name = 'Admin' GROUP BY name;

-- ════════════════════════════════════════════════════════════
-- CASO 3. POST /providers/  (Crear proveedor) - UNIQUE nit y email
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 3: POST /providers/ ===' AS 'PRUEBA';

-- 3.1 FUNCIONALIDAD POSITIVA
START TRANSACTION;
INSERT INTO providers (token, company, nit, email, status, created_at, created_by)
VALUES (UUID(), 'PROVEEDOR QA TEST', '999888777-1', 'qa.proveedor@saip.com', 'ACTIVE', NOW(), 1);
SELECT '3.1 POSITIVO - proveedor insertado:' AS 'VERIFICACION';
SELECT id, company, nit, email, status FROM providers WHERE nit = '999888777-1';
ROLLBACK;

-- 3.2 FUNCIONALIDAD NEGATIVA: viola UNIQUE nit (800123456-1 ya existe, id=1)
START TRANSACTION;
-- ¡ERROR ESPERADO: UNIQUE nit duplicado!
INSERT INTO providers (token, company, nit, email, status, created_at, created_by)
VALUES (UUID(), 'DUPLICADO NIT', '800123456-1', 'dup.nit@saip.com', 'ACTIVE', NOW(), 1);
ROLLBACK;
SELECT '3.2 NEGATIVO - sin duplicado de nit:' AS 'VERIFICACION';
SELECT nit, COUNT(*) AS ocurrencias FROM providers WHERE nit = '800123456-1' GROUP BY nit;

-- ════════════════════════════════════════════════════════════
-- CASO 4. POST /providers/{id}/contacts/  (Contacto de proveedor) - FK a providers
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 4: POST /providers/{id}/contacts/ ===' AS 'PRUEBA';

-- 4.1 FUNCIONALIDAD POSITIVA: proveedor id=1 existe
START TRANSACTION;
INSERT INTO provider_contacts (token, provider_id, name, email, phone, notes, created_at, created_by)
VALUES (UUID(), 1, 'CONTACTO QA', 'contacto.qa@saip.com', '3000000000', 'CONTACTO PRUEBA', NOW(), 1);
SELECT '4.1 POSITIVO - contacto insertado con FK correcta:' AS 'VERIFICACION';
SELECT pc.id, pc.name, pc.email, p.company AS proveedor, p.id AS proveedor_id
FROM provider_contacts pc
JOIN providers p ON p.id = pc.provider_id
WHERE pc.name = 'CONTACTO QA';
ROLLBACK;

-- 4.2 FUNCIONALIDAD NEGATIVA: proveedor inexistente (viola FK)
START TRANSACTION;
-- ¡ERROR ESPERADO: FK provider inexistente 9999!
INSERT INTO provider_contacts (token, provider_id, name, email, phone, notes, created_at, created_by)
VALUES (UUID(), 9999, 'CONTACTO SIN PROV', 'x@saip.com', NULL, NULL, NOW(), 1);
ROLLBACK;
SELECT '4.2 NEGATIVO - sin contacto con FK inválida:' AS 'VERIFICACION';
SELECT COUNT(*) AS filas_con_fk_invalida FROM provider_contacts WHERE provider_id = 9999;

-- ════════════════════════════════════════════════════════════
-- CASO 5. POST /units/  (Crear unidad de medida)
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 5: POST /units/ ===' AS 'PRUEBA';

-- 5.1 FUNCIONALIDAD POSITIVA
START TRANSACTION;
INSERT INTO units (token, name, abbreviation, description, quantity, created_at, created_by)
VALUES (UUID(), 'QUINTAL', 'qq', 'UNIDAD DE PRUEBA QA', 100, NOW(), 1);
SELECT '5.1 POSITIVO - unidad insertada:' AS 'VERIFICACION';
SELECT id, name, abbreviation, quantity FROM units WHERE name = 'QUINTAL';
ROLLBACK;

-- 5.2 FUNCIONALIDAD NEGATIVA: campo obligatorio abbreviation = NULL (NOT NULL)
START TRANSACTION;
-- ¡ERROR ESPERADO: columna abbreviation NOT NULL sin valor!
INSERT INTO units (token, name, abbreviation, description, quantity, created_at, created_by)
VALUES (UUID(), 'UNIDAD SIN ABREV', NULL, 'PRUEBA NEGATIVA', 1, NOW(), 1);
ROLLBACK;
SELECT '5.2 NEGATIVO - no debe persistir unidad sin abbreviation:' AS 'VERIFICACION';
SELECT COUNT(*) AS filas_sin_abrev FROM units WHERE name = 'UNIDAD SIN ABREV';

-- ════════════════════════════════════════════════════════════
-- CASO 6. POST /products/  (Crear producto) - FK a units.id
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 6: POST /products/ ===' AS 'PRUEBA';

-- 6.1 FUNCIONALIDAD POSITIVA: unit_id=9 (UNIDAD) existe
START TRANSACTION;
INSERT INTO products (token, name, description, unit_id, available_quantity, min_stock, max_stock, is_locked, status, created_at, created_by)
VALUES (UUID(), 'PAN TRADICIONAL QA', 'PRODUCTO DE PRUEBA', 9, 500, 10, 1000, 0, 'active', NOW(), 1);
SELECT '6.1 POSITIVO - producto insertado con FK unidad:' AS 'VERIFICACION';
SELECT p.id, p.name, p.unit_id, u.name AS unidad, p.available_quantity, p.status
FROM products p
JOIN units u ON u.id = p.unit_id
WHERE p.name = 'PAN TRADICIONAL QA';
ROLLBACK;

-- 6.2 FUNCIONALIDAD NEGATIVA: unit_id inexistente (viola FK)
START TRANSACTION;
-- ¡ERROR ESPERADO: FK unit inexistente 8888!
INSERT INTO products (token, name, description, unit_id, available_quantity, min_stock, max_stock, is_locked, status, created_at, created_by)
VALUES (UUID(), 'PRODUCTO SIN UNIDAD', NULL, 8888, 0, 0, 0, 0, 'active', NOW(), 1);
ROLLBACK;
SELECT '6.2 NEGATIVO - sin producto con FK inválida:' AS 'VERIFICACION';
SELECT COUNT(*) AS filas_con_fk_invalida FROM products WHERE unit_id = 8888;

-- ════════════════════════════════════════════════════════════
-- CASO 7. POST /supplies/  (Crear insumo) - FK a supply_categories y units
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 7: POST /supplies/ ===' AS 'PRUEBA';

-- 7.1 FUNCIONALIDAD POSITIVA: category_id=1, unit_id=1 existen
START TRANSACTION;
INSERT INTO supplies (token, name, description, category_id, unit_id, available_quantity, min_stock, max_stock, status, created_at, created_by)
VALUES (UUID(), 'AZUCAR BLANCA QA', 'INSUMO DE PRUEBA', 1, 1, 200, 10, 500, 'active', NOW(), 1);
SELECT '7.1 POSITIVO - insumo insertado con FKs:' AS 'VERIFICACION';
SELECT s.id, s.name, s.category_id, sc.name AS categoria, s.unit_id, u.name AS unidad, s.available_quantity
FROM supplies s
JOIN supply_categories sc ON sc.id = s.category_id
JOIN units u ON u.id = s.unit_id
WHERE s.name = 'AZUCAR BLANCA QA';
ROLLBACK;

-- 7.2 FUNCIONALIDAD NEGATIVA: category_id inexistente (viola FK)
START TRANSACTION;
-- ¡ERROR ESPERADO: FK supply_category inexistente 7777!
INSERT INTO supplies (token, name, description, category_id, unit_id, available_quantity, min_stock, max_stock, status, created_at, created_by)
VALUES (UUID(), 'INSUMO SIN CATEGORIA', NULL, 7777, 1, 0, 0, 0, 'active', NOW(), 1);
ROLLBACK;
SELECT '7.2 NEGATIVO - sin insumo con FK inválida:' AS 'VERIFICACION';
SELECT COUNT(*) AS filas_con_fk_invalida FROM supplies WHERE category_id = 7777;

-- ════════════════════════════════════════════════════════════
-- CASO 8. POST /supply-categories/  (Crear categoría de insumo) - UNIQUE name
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 8: POST /supply-categories/ ===' AS 'PRUEBA';

-- 8.1 FUNCIONALIDAD POSITIVA
START TRANSACTION;
INSERT INTO supply_categories (token, name, description, status, created_at, created_by)
VALUES (UUID(), 'ADITIVOS DE PRUEBA QA', 'CATEGORIA DE PRUEBA', 'active', NOW(), 1);
SELECT '8.1 POSITIVO - categoria de insumo insertada:' AS 'VERIFICACION';
SELECT id, name, status FROM supply_categories WHERE name = 'ADITIVOS DE PRUEBA QA';
ROLLBACK;

-- 8.2 FUNCIONALIDAD NEGATIVA: viola UNIQUE name (ADITIVOS id=17 existe)
START TRANSACTION;
-- ¡ERROR ESPERADO: UNIQUE name duplicado!
INSERT INTO supply_categories (token, name, description, status, created_at, created_by)
VALUES (UUID(), 'ADITIVOS', 'DUPLICADO', 'active', NOW(), 1);
ROLLBACK;
SELECT '8.2 NEGATIVO - sin duplicado de categoria:' AS 'VERIFICACION';
SELECT name, COUNT(*) AS ocurrencias FROM supply_categories WHERE name = 'ADITIVOS' GROUP BY name;

-- ════════════════════════════════════════════════════════════
-- CASO 9. POST /product-categories/  (Crear categoría de producto) - UNIQUE name
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 9: POST /product-categories/ ===' AS 'PRUEBA';

-- 9.1 FUNCIONALIDAD POSITIVA
START TRANSACTION;
INSERT INTO product_categories (token, name, description, status, created_at, created_by)
VALUES (UUID(), 'PANADERIA QA', 'CATEGORIA DE PRUEBA', 'active', NOW(), 1);
SELECT '9.1 POSITIVO - categoria de producto insertada:' AS 'VERIFICACION';
SELECT id, name, status FROM product_categories WHERE name = 'PANADERIA QA';
ROLLBACK;

-- 9.2 FUNCIONALIDAD NEGATIVA: viola UNIQUE name (BEBIDAS id=2 existe)
START TRANSACTION;
-- ¡ERROR ESPERADO: UNIQUE name duplicado!
INSERT INTO product_categories (token, name, description, status, created_at, created_by)
VALUES (UUID(), 'BEBIDAS', 'DUPLICADO', 'active', NOW(), 1);
ROLLBACK;
SELECT '9.2 NEGATIVO - sin duplicado de categoria:' AS 'VERIFICACION';
SELECT name, COUNT(*) AS ocurrencias FROM product_categories WHERE name = 'BEBIDAS' GROUP BY name;

-- ════════════════════════════════════════════════════════════
-- CASO 10. POST /commercial-products/  (Producto comercial) - FK category_id, unit_id
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 10: POST /commercial-products/ ===' AS 'PRUEBA';

-- 10.1 FUNCIONALIDAD POSITIVA: category_id=9, unit_id=9 existen
START TRANSACTION;
INSERT INTO commercial_products (token, name, description, category_id, unit_id, purchase_price, sale_price, available_quantity, min_stock, max_stock, status, created_at, created_by)
VALUES (UUID(), 'BEBIDA DE PRUEBA QA', 'PRODUCTO COMERCIAL DE PRUEBA', 9, 9, 2000, 3000, 100, 5, 500, 'active', NOW(), 1);
SELECT '10.1 POSITIVO - producto comercial insertado con FKs:' AS 'VERIFICACION';
SELECT cp.id, cp.name, cp.category_id, pc.name AS categoria, cp.unit_id, u.name AS unidad, cp.sale_price
FROM commercial_products cp
JOIN product_categories pc ON pc.id = cp.category_id
JOIN units u ON u.id = cp.unit_id
WHERE cp.name = 'BEBIDA DE PRUEBA QA';
ROLLBACK;

-- 10.2 FUNCIONALIDAD NEGATIVA: unit_id inexistente (viola FK)
START TRANSACTION;
-- ¡ERROR ESPERADO: FK unit inexistente 5555!
INSERT INTO commercial_products (token, name, description, category_id, unit_id, purchase_price, sale_price, available_quantity, min_stock, max_stock, status, created_at, created_by)
VALUES (UUID(), 'COMERCIAL SIN UNIDAD', NULL, 9, 5555, 0, 0, 0, 0, 0, 'active', NOW(), 1);
ROLLBACK;
SELECT '10.2 NEGATIVO - sin producto comercial con FK inválida:' AS 'VERIFICACION';
SELECT COUNT(*) AS filas_con_fk_invalida FROM commercial_products WHERE unit_id = 5555;

-- ════════════════════════════════════════════════════════════
-- CASO 11. POST /recipes/  (Crear receta) - FK product_id + ingrediente (recipe_ingredients)
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 11: POST /recipes/ ===' AS 'PRUEBA';

-- 11.1 FUNCIONALIDAD POSITIVA: product_id=3, yield_unit_id=9, supply 1, unit 1 existen
START TRANSACTION;
INSERT INTO recipes (token, name, description, product_id, yield_quantity, yield_unit_id, status, created_at, created_by)
VALUES (UUID(), 'RECETA PAN QA', 'RECETA DE PRUEBA', 3, 10, 9, 'ACTIVE', NOW(), 1);
SET @recipe_id = LAST_INSERT_ID();
INSERT INTO recipe_ingredients (token, recipe_id, supply_id, quantity, unit_id, notes)
VALUES (UUID(), @recipe_id, 1, 2, 1, 'INGREDIENTE DE PRUEBA');
SELECT '11.1 POSITIVO - receta insertada con FK y su ingrediente:' AS 'VERIFICACION';
SELECT r.id, r.name, r.product_id, p.name AS producto, r.yield_quantity,
       ri.supply_id, s.name AS insumo, ri.quantity AS cant_insumo
FROM recipes r
JOIN products p ON p.id = r.product_id
LEFT JOIN recipe_ingredients ri ON ri.recipe_id = r.id
LEFT JOIN supplies s ON s.id = ri.supply_id
WHERE r.name = 'RECETA PAN QA';
ROLLBACK;

-- 11.2 FUNCIONALIDAD NEGATIVA: product_id inexistente (viola FK)
START TRANSACTION;
-- ¡ERROR ESPERADO: FK product inexistente 4444!
INSERT INTO recipes (token, name, description, product_id, yield_quantity, yield_unit_id, status, created_at, created_by)
VALUES (UUID(), 'RECETA SIN PRODUCTO', NULL, 4444, 1, 9, 'ACTIVE', NOW(), 1);
ROLLBACK;
SELECT '11.2 NEGATIVO - sin receta con FK inválida:' AS 'VERIFICACION';
SELECT COUNT(*) AS filas_con_fk_invalida FROM recipes WHERE product_id = 4444;

-- FIN DE CASOS CREATE
SELECT '=== FIN EVIDENCIA 01 (CREATE) ===' AS 'FIN';

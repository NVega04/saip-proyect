-- ============================================================
-- PROYECTO DE GRADO: SAIP
-- EVIDENCIA 02: CASOS DE PRUEBA - OPERACIONES UPDATE (PATCH/PUT)
-- Punto 3.4 - Paso 3 y 4
-- Endpoints UPDATE x 2 funcionalidades
-- ============================================================
-- POSITIVO: UPDATE válido -> SELECT verifica cambio -> ROLLBACK
-- NEGATIVO: UPDATE que viola UNIQUE/FK -> la BD lo rechaza -> SELECT certifica sin cambio
-- ============================================================

-- ════════════════════════════════════════════════════════════
-- CASO 12. PUT /users/{id}  (Actualizar usuario) - UNIQUE email
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 12: PUT /users/{id} ===' AS 'PRUEBA';

-- 12.1 FUNCIONALIDAD POSITIVA: actualizar first_name / role_id del usuario id=1
START TRANSACTION;
UPDATE users SET first_name = 'ADMIN ACTUALIZADO', role_id = 1, updated_at = NOW(), updated_by = 1
WHERE id = 1 AND deleted_at IS NULL;
SELECT '12.1 POSITIVO - usuario actualizado:' AS 'VERIFICACION';
SELECT id, first_name, last_name, email, role_id, status FROM users WHERE id = 1;
ROLLBACK; -- revierte el cambio de prueba

-- 12.2 FUNCIONALIDAD NEGATIVA: asignar email duplicado (el de otro usuario) -> la app devuelve 409
START TRANSACTION;
-- Se usa un usuario de respaldo para no romper datos reales
INSERT INTO users (token, first_name, last_name, email, password_hash, role_id, status, is_admin, accepted_terms, created_at)
SELECT UUID(), 'RESPALDO', 'QA', 'respaldo.qa@saip.com', 'x', 1, 'ACTIVE', 0, 1, NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'respaldo.qa@saip.com');
SET @id_respaldo = LAST_INSERT_ID();
-- ¡ERROR ESPERADO: UNIQUE email duplicado al intentar igualar a admin@saip.com!
UPDATE users SET email = 'admin@saip.com', updated_at = NOW() WHERE id = @id_respaldo;
SELECT '12.2 NEGATIVO - verificación (email admin debe ser unico):' AS 'VERIFICACION';
SELECT email, COUNT(*) AS ocurrencias FROM users WHERE email = 'admin@saip.com' GROUP BY email;
ROLLBACK;

-- ════════════════════════════════════════════════════════════
-- CASO 13. PATCH /roles/{id}  (Actualizar rol) - UNIQUE name
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 13: PATCH /roles/{id} ===' AS 'PRUEBA';

-- 13.1 FUNCIONALIDAD POSITIVA: crear rol temporal, actualizar descripción
START TRANSACTION;
INSERT INTO roles (token, name, description, status, created_at)
VALUES (UUID(), 'ROL UPDATE QA', 'DESCRIPCION ORIGINAL', 'ACTIVE', NOW());
SET @rol_id = LAST_INSERT_ID();
UPDATE roles SET description = 'DESCRIPCION ACTUALIZADA', updated_at = NOW() WHERE id = @rol_id;
SELECT '13.1 POSITIVO - rol actualizado:' AS 'VERIFICACION';
SELECT id, name, description, status FROM roles WHERE id = @rol_id;
ROLLBACK;

-- 13.2 FUNCIONALIDAD NEGATIVA: renombrar a un name ya existente (duplica 'Admin')
START TRANSACTION;
INSERT INTO roles (token, name, description, status, created_at)
VALUES (UUID(), 'ROL QA UNICO', 'PRUEBA', 'ACTIVE', NOW());
SET @rol_id2 = LAST_INSERT_ID();
-- ¡ERROR ESPERADO: la app valida UNIQUE name y devuelve 409; en BD el UNIQUE name no existe como constraint, depende de la app
UPDATE roles SET name = 'Admin', updated_at = NOW() WHERE id = @rol_id2;
SELECT '13.2 NEGATIVO - verificacion de duplicado de nombre:' AS 'VERIFICACION';
SELECT name, COUNT(*) AS ocurrencias FROM roles WHERE name = 'Admin' GROUP BY name;
ROLLBACK;

-- ════════════════════════════════════════════════════════════
-- CASO 14. PATCH /providers/{id}  (Actualizar proveedor) - UNIQUE nit y email
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 14: PATCH /providers/{id} ===' AS 'PRUEBA';

-- 14.1 FUNCIONALIDAD POSITIVA: actualizar company del proveedor id=1
START TRANSACTION;
UPDATE providers SET company = 'HARINERA DEL VALLE ACTUALIZADO', updated_at = NOW() WHERE id = 1;
SELECT '14.1 POSITIVO - proveedor actualizado:' AS 'VERIFICACION';
SELECT id, company, nit, email, status FROM providers WHERE id = 1;
ROLLBACK;

-- 14.2 FUNCIONALIDAD NEGATIVA: asignar nit duplicado (800234567-2 pertenece a otro)
START TRANSACTION;
-- ¡ERROR ESPERADO: la app valida UNIQUE nit y devuelve 409!
UPDATE providers SET nit = '800234567-2', updated_at = NOW() WHERE id = 1;
SELECT '14.2 NEGATIVO - verificacion de duplicado de nit:' AS 'VERIFICACION';
SELECT nit, COUNT(*) AS ocurrencias FROM providers WHERE nit = '800234567-2' GROUP BY nit;
ROLLBACK;

-- ════════════════════════════════════════════════════════════
-- CASO 15. PATCH /units/{id}  (Actualizar unidad de medida)
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 15: PATCH /units/{id} ===' AS 'PRUEBA';

-- 15.1 FUNCIONALIDAD POSITIVA: actualizar la unidad id=1 (temporal)
START TRANSACTION;
UPDATE units SET name = 'KILOGRAMO ACTUALIZADO', updated_at = NOW() WHERE id = 1;
SELECT '15.1 POSITIVO - unidad actualizada:' AS 'VERIFICACION';
SELECT id, name, abbreviation, quantity FROM units WHERE id = 1;
ROLLBACK;

-- 15.2 FUNCIONALIDAD NEGATIVA: intentar actualizar a un id inexistente
START TRANSACTION;
UPDATE units SET name = 'NO EXISTE' WHERE id = 99999;
SELECT '15.2 NEGATIVO - filas afectadas deben ser 0 (id inexistente):' AS 'VERIFICACION';
SELECT ROW_COUNT() AS filas_afectadas;
ROLLBACK;
SELECT '15.2 NEGATIVO - verificar que no existe la unidad:' AS 'VERIFICACION';
SELECT COUNT(*) AS filas FROM units WHERE id = 99999;

-- FIN EVIDENCIA 02
SELECT '=== FIN EVIDENCIA 02 (UPDATE) ===' AS 'FIN';

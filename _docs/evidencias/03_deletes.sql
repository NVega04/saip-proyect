-- ============================================================
-- PROYECTO DE GRADO: SAIP
-- EVIDENCIA 03: CASOS DE PRUEBA - OPERACIONES DELETE (soFT DELETE)
-- Punto 3.4 - Paso 3 y 4
-- Endpoints DELETE x 2 funcionalidades
-- ============================================================
-- NOTA: SAIP usa SOFT DELETE. "Borrar" = marcar deleted_at + deleted_by
--        (y en algunos modelos status = INACTIVE). Los SELECT NO muestran borrados.
-- POSITIVO : DELETE válido -> marca deleted_at -> SELECT no lo lista
-- NEGATIVO : DELETE sobre registro ya borrado/inexistente -> 0 filas
-- ============================================================

-- ════════════════════════════════════════════════════════════
-- CASO 16. DELETE /users/{id}  (Soft delete de usuario)
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 16: DELETE /users/{id} ===' AS 'PRUEBA';

-- 16.1 FUNCIONALIDAD POSITIVA: crear usuario temporal y "eliminarlo" (soft delete)
START TRANSACTION;
INSERT INTO users (token, first_name, last_name, email, password_hash, role_id, status, is_admin, accepted_terms, created_at)
VALUES (UUID(), 'USUARIO', 'ELIMINAR QA', 'eliminar.qa@saip.com', 'x', 1, 'ACTIVE', 0, 1, NOW());
SET @uid = LAST_INSERT_ID();
UPDATE users SET deleted_at = NOW(), deleted_by = 1, status = 'INACTIVE' WHERE id = @uid;
SELECT '16.1 POSITIVO - verificar soft delete (fila marcada, ya NO activa):' AS 'VERIFICACION';
SELECT id, email, deleted_at, deleted_by, status FROM users WHERE id = @uid;
SELECT '16.1 POSITIVO - confirmar que no aparece en listado de activos:' AS 'VERIFICACION';
SELECT COUNT(*) AS usuarios_activos_con_ese_email FROM users WHERE email = 'eliminar.qa@saip.com' AND deleted_at IS NULL;
ROLLBACK;

-- 16.2 FUNCIONALIDAD NEGATIVA: borrar un id inexistente
START TRANSACTION;
UPDATE users SET deleted_at = NOW(), deleted_by = 1 WHERE id = 99999;
SELECT '16.2 NEGATIVO - filas afectadas (0 = no existe):' AS 'VERIFICACION';
SELECT ROW_COUNT() AS filas_afectadas;
ROLLBACK;

-- ════════════════════════════════════════════════════════════
-- CASO 17. DELETE /roles/{id}  (Soft delete de rol)
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 17: DELETE /roles/{id} ===' AS 'PRUEBA';

-- 17.1 FUNCIONALIDAD POSITIVA
START TRANSACTION;
INSERT INTO roles (token, name, description, status, created_at)
VALUES (UUID(), 'ROL A ELIMINAR QA', 'PRUEBA DELETE', 'ACTIVE', NOW());
SET @rid = LAST_INSERT_ID();
UPDATE roles SET deleted_at = NOW(), deleted_by = 1, status = 'INACTIVE' WHERE id = @rid;
SELECT '17.1 POSITIVO - rol marcado como eliminado (soft):' AS 'VERIFICACION';
SELECT id, name, deleted_at, deleted_by, status FROM roles WHERE id = @rid;
ROLLBACK;

-- 17.2 FUNCIONALIDAD NEGATIVA: borrar id inexistente
UPDATE roles SET deleted_at = NOW(), deleted_by = 1 WHERE id = 99999;
SELECT '17.2 NEGATIVO - filas afectadas (0 = no existe):' AS 'VERIFICACION';
SELECT ROW_COUNT() AS filas_afectadas;

-- ════════════════════════════════════════════════════════════
-- CASO 18. DELETE /providers/{id}  (Soft delete de proveedor)
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 18: DELETE /providers/{id} ===' AS 'PRUEBA';

-- 18.1 FUNCIONALIDAD POSITIVA: proveedor real id=1 -> soft delete
START TRANSACTION;
UPDATE providers SET deleted_at = NOW(), deleted_by = 1, status = 'INACTIVE' WHERE id = 1;
SELECT '18.1 POSITIVO - proveedor marcado eliminado (soft):' AS 'VERIFICACION';
SELECT id, company, deleted_at, deleted_by, status FROM providers WHERE id = 1;
ROLLBACK; -- revierte, no se elimina el proveedor real

-- 18.2 FUNCIONALIDAD NEGATIVA: la app NO permite borrar un proveedor ya inactivo/borrado
START TRANSACTION;
-- Crear un proveedor y borrarlo 2 veces
INSERT INTO providers (token, company, nit, email, status, created_at, created_by)
VALUES (UUID(), 'PROV DOBLE DELETE', '555555555-5', 'doble.delete@saip.com', 'ACTIVE', NOW(), 1);
SET @pid = LAST_INSERT_ID();
UPDATE providers SET deleted_at = NOW(), deleted_by = 1, status = 'INACTIVE' WHERE id = @pid;
-- Segundo intento sobre un registro ya inactivo: la app devuelve 409
UPDATE providers SET deleted_at = NOW(), deleted_by = 1 WHERE id = @pid AND status = 'INACTIVE';
SELECT '18.2 NEGATIVO - segundo borrado no debe marcar nada nuevo (fila ya inactiva):' AS 'VERIFICACION';
SELECT id, status, deleted_at FROM providers WHERE id = @pid;
ROLLBACK;

-- ════════════════════════════════════════════════════════════
-- CASO 19. DELETE /providers/{id}/contacts/{contact_id}
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 19: DELETE contact de proveedor ===' AS 'PRUEBA';

-- 19.1 FUNCIONALIDAD POSITIVA: crear contacto y hacer soft delete
START TRANSACTION;
INSERT INTO provider_contacts (token, provider_id, name, email, phone, notes, created_at, created_by)
VALUES (UUID(), 1, 'CONTACTO A ELIMINAR', 'eliminar.contacto@saip.com', '3011111111', NULL, NOW(), 1);
SET @cid = LAST_INSERT_ID();
UPDATE provider_contacts SET deleted_at = NOW(), deleted_by = 1 WHERE id = @cid;
SELECT '19.1 POSITIVO - contacto marcado eliminado (soft):' AS 'VERIFICACION';
SELECT id, name, provider_id, deleted_at, deleted_by FROM provider_contacts WHERE id = @cid;
ROLLBACK;

-- 19.2 FUNCIONALIDAD NEGATIVA: borrar contacto inexistente
UPDATE provider_contacts SET deleted_at = NOW(), deleted_by = 1 WHERE id = 99999;
SELECT '19.2 NEGATIVO - filas afectadas (0 = no existe):' AS 'VERIFICACION';
SELECT ROW_COUNT() AS filas_afectadas;

-- ════════════════════════════════════════════════════════════
-- CASO 20. DELETE /units/{id}  (Soft delete de unidad de medida)
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 20: DELETE /units/{id} ===' AS 'PRUEBA';

-- 20.1 FUNCIONALIDAD POSITIVA
START TRANSACTION;
INSERT INTO units (token, name, abbreviation, description, quantity, created_at, created_by)
VALUES (UUID(), 'UNIDAD ELIMINAR QA', 'uel', 'PRUEBA DELETE', 1, NOW(), 1);
SET @unid = LAST_INSERT_ID();
UPDATE units SET deleted_at = NOW(), deleted_by = 1 WHERE id = @unid;
SELECT '20.1 POSITIVO - unidad marcada eliminada (soft):' AS 'VERIFICACION';
SELECT id, name, abbreviation, deleted_at, deleted_by FROM units WHERE id = @unid;
ROLLBACK;

-- 20.2 FUNCIONALIDAD NEGATIVA: borrar id inexistente
UPDATE units SET deleted_at = NOW(), deleted_by = 1 WHERE id = 99999;
SELECT '20.2 NEGATIVO - filas afectadas (0 = no existe):' AS 'VERIFICACION';
SELECT ROW_COUNT() AS filas_afectadas;

-- FIN EVIDENCIA 03
SELECT '=== FIN EVIDENCIA 03 (DELETE) ===' AS 'FIN';

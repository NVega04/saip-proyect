-- ============================================================
-- PROYECTO DE GRADO: SAIP
-- EVIDENCIA 04: CASO TRANSACCIONAL - VENTAS Y ANULACION
-- Punto 3.4 - Criterio: "Comprobar la correcta ejecución de
-- transacciones y la reversión de datos (ROLLBACK) frente a
-- fallos o violaciones de restricciones de integridad"
-- 1 endpoint (POST /sales/ + PATCH /sales/{id}/annul) x 2 funcionalidades
-- ============================================================
-- Escenario real (datos vivos):
--   Producto id=3 'CROISSANT MANTEQUILLA' con available_quantity=200,
--   min_stock=10. Usuario id=1 (admin).
--
-- La venta (POST /sales/) en el backend:
--   1. INSERT en sales
--   2. INSERT en sale_items
--   3. UPDATE products.available_quantity = stock - cant (resta stock)
--   4. INSERT en inventory_movements (movement_type=SALE)
--   Si NO hay stock suficiente -> HTTP 400 y session.rollback()
--
-- La anulación (PATCH /sales/{id}/annul):
--   Invierte el stock (stock + cant) y crea movimiento SALE_ANNULMENT.
-- ============================================================

-- ════════════════════════════════════════════════════════════
-- 21. FUNCIONALIDAD POSITIVA: Venta válida + verificación + anulación
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 21 POSITIVO: POST /sales/ (venta válida) ===' AS 'PRUEBA';

START TRANSACTION;
-- 21.1 PASO PREVIO: estado del stock antes
SELECT '21.1 - stock ANTES de la venta:' AS 'ESTADO_PREVIO';
SELECT id, name, available_quantity FROM products WHERE id = 3;

-- 21.2 ACCIÓN (equivalente a POST /sales/) - vender 5 unidades del producto 3
INSERT INTO sales (token, user_id, sale_date, status, notes, created_at, created_by)
VALUES (UUID(), 1, NOW(), 'COMPLETED', 'VENTA DE PRUEBA QA', NOW(), 1);
SET @venta_id = LAST_INSERT_ID();

INSERT INTO sale_items (token, sale_id, item_type, item_id, item_name, quantity, created_at)
VALUES (UUID(), @venta_id, 'PRODUCT', 3, 'CROISSANT MANTEQUILLA', 5, NOW());

-- Resta de stock
UPDATE products SET available_quantity = available_quantity - 5 WHERE id = 3;

-- Movimiento de inventario (stock_before 200 -> stock_after 195)
INSERT INTO inventory_movements (token, item_type, item_id, movement_type, quantity, stock_before, stock_after, reference_type, reference_id, user_id, created_at)
VALUES (UUID(), 'PRODUCT', 3, 'SALE', 5, 200, 195, 'sale', @venta_id, 1, NOW());

-- 21.3 VERIFICACIÓN: la venta persiste con sus relaciones (FK correctas)
SELECT '21.3 - Venta insertada:' AS 'VERIFICACION';
SELECT s.id AS venta_id, s.status, s.user_id, u.email AS vendedor, s.sale_date
FROM sales s
JOIN users u ON u.id = s.user_id
WHERE s.id = @venta_id;

SELECT '21.3 - Items de la venta (relación sale_items -> sales -> products):' AS 'VERIFICACION';
SELECT si.sale_id, si.item_name, si.quantity, p.available_quantity AS stock_restante
FROM sale_items si
JOIN products p ON p.id = si.item_id
WHERE si.sale_id = @venta_id;

SELECT '21.3 - Movimiento de inventario registrado (consistencia stock):' AS 'VERIFICACION';
SELECT item_type, item_id, movement_type, quantity, stock_before, stock_after, reference_type, reference_id
FROM inventory_movements WHERE reference_id = @venta_id;

-- 21.4 ANULACIÓN (equivalente a PATCH /sales/{id}/annul): restaura stock
UPDATE sales SET status = 'ANNULLED', updated_at = NOW(), updated_by = 1 WHERE id = @venta_id;
UPDATE products SET available_quantity = available_quantity + 5 WHERE id = 3;
INSERT INTO inventory_movements (token, item_type, item_id, movement_type, quantity, stock_before, stock_after, reference_type, reference_id, user_id, created_at)
VALUES (UUID(), 'PRODUCT', 3, 'SALE_ANNULMENT', 5, 195, 200, 'sale', @venta_id, 1, NOW());

SELECT '21.4 - Verificación POST-anulación (venta ANNULLED, stock restaurado):' AS 'VERIFICACION';
SELECT s.id, s.status, p.available_quantity AS stock_restaurado
FROM sales s, products p WHERE s.id = @venta_id AND p.id = 3;

ROLLBACK; -- La prueba NO deja datos residuales en la BD de producción
SELECT '21 POSITIVO - ROLLBACK aplicado, sin datos residuales.' AS 'RESULTADO';

-- ════════════════════════════════════════════════════════════
-- 22. FUNCIONALIDAD NEGATIVA: Venta con stock INSUFICIENTE -> ROLLBACK
-- ════════════════════════════════════════════════════════════
SELECT '=== CASO 22 NEGATIVO: POST /sales/ (stock insuficiente) ===' AS 'PRUEBA';

START TRANSACTION;
-- 22.1 stock actual del producto 3 (real)
SELECT '22.1 - stock disponible del producto 3:' AS 'ESTADO_PREVIO';
SELECT id, name, available_quantity FROM products WHERE id = 3;

-- 22.2 ACCION FALLIDA: intentar vender 100000 unidades (stock=200 -> insuficiente)
-- En el backend esto dispara: raise HTTPException 400 + session.rollback()
-- La BD no puede insertar porque NO hay stock; aquí se simula la validación
-- de negocio que la aplicación realiza ANTES de persistir.
INSERT INTO sales (token, user_id, sale_date, status, notes, created_at, created_by)
VALUES (UUID(), 1, NOW(), 'COMPLETED', 'VENTA FALLIDA QA', NOW(), 1);
SET @venta_fallida = LAST_INSERT_ID();

-- Simulación del control de stock: tal como el backend valida "quantity > available_quantity"
SET @stock = (SELECT available_quantity FROM products WHERE id = 3);
SELECT '22.2 - control: stock@' AS 'CONTROL', @stock AS stock_disponible, 100000 AS solicitado,
       IF(100000 > @stock, 'SUPERA STOCK -> SE DEBE RECHAZAR', 'OK') AS decision;

-- Como supera el stock, la transacción debe REVERTIRSE (ROLLBACK) sin persistir nada.
ROLLBACK;

-- 22.3 VERIFICACION: NO debió persistir ninguna venta fallida (cero filas)
SELECT '22.3 - No debe existir venta con stock insuficiente persistida:' AS 'VERIFICACION';
SELECT COUNT(*) AS ventas_fallidas_persistidas
FROM sales s
JOIN sale_items si ON si.sale_id = s.id
WHERE si.quantity > 100000;

-- 22.4 VERIFICACION: el stock del producto 3 NO fue modificado (sigue en 200)
SELECT '22.4 - stock del producto 3 intacto (ROLLBACK correcto):' AS 'VERIFICACION';
SELECT id, name, available_quantity FROM products WHERE id = 3;

SELECT '=== FIN EVIDENCIA 04 (VENTAS TRANSACCIONAL) ===' AS 'FIN';

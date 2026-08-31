-- ============================================================
-- SAIP — Seed de Datos v4
-- Incluye: sales, sale_items, inventory_movements
-- ProductionOrder actualizado: started_at, cancelled_at
-- Todos los nombres en MAYÚSCULA
-- 20 registros por tabla donde aplica
-- Ejecutar DESPUÉS del TRUNCATE completo
-- ============================================================

/*!40101 SET NAMES utf8mb4 */;

-- ============================================================
-- TRUNCATE PREVIO (limpia todas las tablas en orden seguro)
-- ============================================================
SET FOREIGN_KEY_CHECKS=0;
TRUNCATE TABLE inventory_movements;
TRUNCATE TABLE sale_items;
TRUNCATE TABLE sales;
TRUNCATE TABLE production_order_snapshots;
TRUNCATE TABLE production_orders;
TRUNCATE TABLE recipe_ingredients;
TRUNCATE TABLE recipes;
TRUNCATE TABLE commercial_products;
TRUNCATE TABLE product_categories;
TRUNCATE TABLE products;
TRUNCATE TABLE supplies;
TRUNCATE TABLE supply_categories;
TRUNCATE TABLE units;
TRUNCATE TABLE provider_contacts;
TRUNCATE TABLE providers;
TRUNCATE TABLE role_modules;
TRUNCATE TABLE modules;
TRUNCATE TABLE password_resets;
TRUNCATE TABLE sessions;
TRUNCATE TABLE users;
TRUNCATE TABLE roles;
SET FOREIGN_KEY_CHECKS=1;
/*!40014 SET FOREIGN_KEY_CHECKS=0 */;

-- ============================================================
-- 1. ROLES (20)
-- ============================================================
INSERT INTO roles (token, name, description, created_at, status) VALUES
(UUID(), 'DUEÑO',                  'ACCESO TOTAL AL SISTEMA, FINANZAS, PERSONAL E INVENTARIO',          NOW(), 'active'),
(UUID(), 'GERENTE DE TIENDA',      'SUPERVISIÓN DE VENTAS DIARIAS Y ATENCIÓN AL CLIENTE',               NOW(), 'active'),
(UUID(), 'MAESTRO PANADERO',       'RESPONSABLE DE LA PRODUCCIÓN PRINCIPAL Y RECETAS DE PAN',           NOW(), 'active'),
(UUID(), 'MAESTRO PASTELERO',      'ESPECIALISTA EN DECORACIÓN, TORTAS Y REPOSTERÍA FINA',              NOW(), 'active'),
(UUID(), 'AYUDANTE DE PANADERÍA',  'APOYO EN AMASADO, HORNEADO Y LIMPIEZA DE ÁREA',                     NOW(), 'active'),
(UUID(), 'AYUDANTE DE PASTELERÍA', 'PREPARACIÓN DE RELLENOS, BATIDOS Y DECORACIONES BÁSICAS',           NOW(), 'active'),
(UUID(), 'HORNERO',                'CONTROL EXCLUSIVO DE TIEMPOS Y TEMPERATURAS DE COCCIÓN',            NOW(), 'active'),
(UUID(), 'ENCARGADO DE INVENTARIO','GESTIÓN DE MATERIA PRIMA: HARINAS, LEVADURAS, AZÚCARES',            NOW(), 'active'),
(UUID(), 'CAJERO PRINCIPAL',       'CIERRE DE CAJA, ARQUEOS Y MANEJO DE EFECTIVO',                      NOW(), 'active'),
(UUID(), 'VENDEDOR DE MOSTRADOR',  'ATENCIÓN DIRECTA AL PÚBLICO Y DESPACHO DE PRODUCTOS',               NOW(), 'active'),
(UUID(), 'REPOSTERO DE VITRINA',   'MONTAJE Y ESTÉTICA DE PRODUCTOS EN EL ÁREA DE VENTA',               NOW(), 'active'),
(UUID(), 'CONTROL DE CALIDAD',     'REVISIÓN DE FRESCURA, SABOR Y ESTÁNDARES DE HIGIENE',               NOW(), 'active'),
(UUID(), 'REPARTIDOR / DELIVERY',  'ENTREGA DE PEDIDOS A DOMICILIO Y EVENTOS EXTERNOS',                 NOW(), 'active'),
(UUID(), 'ENCARGADO DE COMPRAS',   'NEGOCIACIÓN CON PROVEEDORES Y RECEPCIÓN DE INSUMOS',                NOW(), 'active'),
(UUID(), 'PERSONAL DE LIMPIEZA',   'MANTENIMIENTO SANITARIO DE ÁREAS DE PRODUCCIÓN Y SALÓN',            NOW(), 'active'),
(UUID(), 'MESERO',                 'ATENCIÓN EN MESAS PARA PANADERÍAS CON ZONA DE CAFÉ',                NOW(), 'active'),
(UUID(), 'BARISTA',                'PREPARACIÓN DE CAFÉS Y BEBIDAS PARA ACOMPAÑAR EL PAN',              NOW(), 'active'),
(UUID(), 'SEGURIDAD',              'VIGILANCIA DEL LOCAL Y CONTROL DE ACCESOS',                         NOW(), 'active'),
(UUID(), 'EDITOR DE MENÚ',         'GESTIÓN DE PRECIOS Y PRODUCTOS EN EL SISTEMA',                      NOW(), 'active'),
(UUID(), 'APRENDIZ / PASANTE',     'ROL DE FORMACIÓN CON PERMISOS LIMITADOS EN EL SISTEMA',             NOW(), 'active');

-- ============================================================
-- 2. USERS (20)
-- ============================================================
INSERT INTO users (token, first_name, last_name, email, phone, password_hash,
                   created_at, status, is_admin, role_id,
                   accepted_terms, accepted_terms_at) VALUES
(UUID(), 'JUAN',     'PÉREZ',      'juan.perez@saip.com',      '3001110101', '$2b$12$dummyhash00000000000001', NOW(), 'active', 1,  1, 1, NOW()),
(UUID(), 'MARÍA',    'GARCÍA',     'm.garcia@saip.com',        '3001110102', '$2b$12$dummyhash00000000000002', NOW(), 'active', 1,  2, 1, NOW()),
(UUID(), 'CARLOS',   'LÓPEZ',      'c.lopez@saip.com',         '3001110103', '$2b$12$dummyhash00000000000003', NOW(), 'active', 0,  3, 1, NOW()),
(UUID(), 'ANA',      'MARTÍNEZ',   'a.martinez@saip.com',      '3001110104', '$2b$12$dummyhash00000000000004', NOW(), 'active', 0,  4, 1, NOW()),
(UUID(), 'LUIS',     'RODRÍGUEZ',  'l.rodriguez@saip.com',     '3001110105', '$2b$12$dummyhash00000000000005', NOW(), 'active', 0,  5, 1, NOW()),
(UUID(), 'ELENA',    'SÁNCHEZ',    'e.sanchez@saip.com',       '3001110106', '$2b$12$dummyhash00000000000006', NOW(), 'active', 0,  9, 1, NOW()),
(UUID(), 'PEDRO',    'RAMÍREZ',    'p.ramirez@saip.com',       '3001110107', '$2b$12$dummyhash00000000000007', NOW(), 'active', 0, 10, 1, NOW()),
(UUID(), 'SOFÍA',    'TORRES',     's.torres@saip.com',        '3001110108', '$2b$12$dummyhash00000000000008', NOW(), 'active', 0,  7, 1, NOW()),
(UUID(), 'DIEGO',    'FLORES',     'd.flores@saip.com',        '3001110109', '$2b$12$dummyhash00000000000009', NOW(), 'active', 0, 13, 1, NOW()),
(UUID(), 'LUCÍA',    'GÓMEZ',      'l.gomez@saip.com',         '3001110110', '$2b$12$dummyhash00000000000010', NOW(), 'active', 0,  6, 1, NOW()),
(UUID(), 'ROBERTO',  'DÍAZ',       'r.diaz@saip.com',          '3001110111', '$2b$12$dummyhash00000000000011', NOW(), 'active', 0,  8, 1, NOW()),
(UUID(), 'CARMEN',   'RUIZ',       'c.ruiz@saip.com',          '3001110112', '$2b$12$dummyhash00000000000012', NOW(), 'active', 0, 15, 0, NULL),
(UUID(), 'MIGUEL',   'HERNÁNDEZ',  'm.hernandez@saip.com',     '3001110113', '$2b$12$dummyhash00000000000013', NOW(), 'active', 0, 17, 1, NOW()),
(UUID(), 'LAURA',    'CASTRO',     'l.castro@saip.com',        '3001110114', '$2b$12$dummyhash00000000000014', NOW(), 'active', 0, 10, 1, NOW()),
(UUID(), 'ANDRÉS',   'MORALES',    'a.morales@saip.com',       '3001110115', '$2b$12$dummyhash00000000000015', NOW(), 'active', 0, 14, 1, NOW()),
(UUID(), 'RICARDO',  'VARGAS',     'r.vargas@saip.com',        '3001110116', '$2b$12$dummyhash00000000000016', NOW(), 'active', 0, 12, 0, NULL),
(UUID(), 'PATRICIA', 'LUNA',       'p.luna@saip.com',          '3001110117', '$2b$12$dummyhash00000000000017', NOW(), 'active', 0, 11, 1, NOW()),
(UUID(), 'FERNANDO', 'SOTO',       'f.soto@saip.com',          '3001110118', '$2b$12$dummyhash00000000000018', NOW(), 'active', 0, 16, 0, NULL),
(UUID(), 'MÓNICA',   'HERRERA',    'm.herrera@saip.com',       '3001110119', '$2b$12$dummyhash00000000000019', NOW(), 'active', 0, 15, 1, NOW()),
(UUID(), 'GABRIEL',  'MENDOZA',    'g.mendoza@saip.com',       '3001110120', '$2b$12$dummyhash00000000000020', NOW(), 'active', 0, 20, 1, NOW());

-- ============================================================
-- 3. MODULES (20)
-- ============================================================
INSERT INTO modules (token, name, label) VALUES
(UUID(), 'dashboard',     'PANEL PRINCIPAL'),
(UUID(), 'users',         'USUARIOS'),
(UUID(), 'roles',         'ROLES'),
(UUID(), 'inventory',     'INVENTARIO'),
(UUID(), 'supplies',      'INSUMOS'),
(UUID(), 'products',      'PRODUCTOS'),
(UUID(), 'recipes',       'RECETAS'),
(UUID(), 'production',    'PRODUCCIÓN'),
(UUID(), 'providers',     'PROVEEDORES'),
(UUID(), 'purchases',     'COMPRAS'),
(UUID(), 'sales',         'VENTAS'),
(UUID(), 'cash',          'CAJA'),
(UUID(), 'reports',       'REPORTES'),
(UUID(), 'quality',       'CONTROL DE CALIDAD'),
(UUID(), 'delivery',      'DOMICILIOS'),
(UUID(), 'menu',          'MENÚ / CARTA'),
(UUID(), 'notifications', 'NOTIFICACIONES'),
(UUID(), 'audit',         'AUDITORÍA'),
(UUID(), 'settings',      'CONFIGURACIÓN'),
(UUID(), 'support',       'SOPORTE');

-- ============================================================
-- 4. ROLE_MODULES (20)
-- ============================================================
INSERT INTO role_modules (token, role_id, module_id) VALUES
(UUID(), 1,  1),(UUID(), 1,  2),(UUID(), 1,  3),(UUID(), 1, 13),
(UUID(), 1, 19),(UUID(), 1, 18),
(UUID(), 2,  1),(UUID(), 2, 11),(UUID(), 2, 12),(UUID(), 2, 13),
(UUID(), 3,  7),(UUID(), 3,  8),(UUID(), 3,  5),
(UUID(), 8,  4),(UUID(), 8,  5),(UUID(), 8,  9),(UUID(), 8, 10),
(UUID(), 9,  1),(UUID(), 9, 11),(UUID(), 9, 12);

-- ============================================================
-- 5. SESSIONS (20)
-- ============================================================
INSERT INTO sessions (token, user_id, created_at, expires_at, is_active) VALUES
(UUID(),  1, NOW()-INTERVAL 30 MINUTE, NOW()+INTERVAL 7 HOUR,  1),
(UUID(),  2, NOW()-INTERVAL 1  HOUR,   NOW()+INTERVAL 6 HOUR,  1),
(UUID(),  3, NOW()-INTERVAL 2  HOUR,   NOW()+INTERVAL 5 HOUR,  1),
(UUID(),  4, NOW()-INTERVAL 3  HOUR,   NOW()+INTERVAL 4 HOUR,  1),
(UUID(),  5, NOW()-INTERVAL 4  HOUR,   NOW()+INTERVAL 3 HOUR,  1),
(UUID(),  6, NOW()-INTERVAL 5  HOUR,   NOW()+INTERVAL 2 HOUR,  1),
(UUID(),  7, NOW()-INTERVAL 6  HOUR,   NOW()+INTERVAL 1 HOUR,  1),
(UUID(),  8, NOW()-INTERVAL 7  HOUR,   NOW()-INTERVAL 1 HOUR,  0),
(UUID(),  9, NOW()-INTERVAL 8  HOUR,   NOW()-INTERVAL 2 HOUR,  0),
(UUID(), 10, NOW()-INTERVAL 9  HOUR,   NOW()-INTERVAL 3 HOUR,  0),
(UUID(), 11, NOW()-INTERVAL 10 HOUR,   NOW()-INTERVAL 4 HOUR,  0),
(UUID(), 12, NOW()-INTERVAL 11 HOUR,   NOW()-INTERVAL 5 HOUR,  0),
(UUID(), 13, NOW()-INTERVAL 12 HOUR,   NOW()-INTERVAL 6 HOUR,  0),
(UUID(), 14, NOW()-INTERVAL 1  DAY,    NOW()-INTERVAL 16 HOUR, 0),
(UUID(), 15, NOW()-INTERVAL 1  DAY,    NOW()-INTERVAL 15 HOUR, 0),
(UUID(), 16, NOW()-INTERVAL 2  DAY,    NOW()-INTERVAL 39 HOUR, 0),
(UUID(), 17, NOW()-INTERVAL 2  DAY,    NOW()-INTERVAL 38 HOUR, 0),
(UUID(), 18, NOW()-INTERVAL 3  DAY,    NOW()-INTERVAL 63 HOUR, 0),
(UUID(), 19, NOW()-INTERVAL 3  DAY,    NOW()-INTERVAL 62 HOUR, 0),
(UUID(), 20, NOW()-INTERVAL 4  DAY,    NOW()-INTERVAL 87 HOUR, 0);

-- ============================================================
-- 6. PASSWORD_RESETS (20)
-- ============================================================
INSERT INTO password_resets (token, user_id, expires_at, created_at, used) VALUES
(UUID(),  1, NOW()+INTERVAL 1 HOUR,   NOW(), 0),
(UUID(),  2, NOW()+INTERVAL 1 HOUR,   NOW(), 0),
(UUID(),  3, NOW()-INTERVAL 2 HOUR,   NOW()-INTERVAL 3 HOUR, 1),
(UUID(),  4, NOW()-INTERVAL 2 HOUR,   NOW()-INTERVAL 3 HOUR, 1),
(UUID(),  5, NOW()-INTERVAL 5 HOUR,   NOW()-INTERVAL 6 HOUR, 0),
(UUID(),  6, NOW()-INTERVAL 5 HOUR,   NOW()-INTERVAL 6 HOUR, 0),
(UUID(),  7, NOW()+INTERVAL 30 MINUTE,NOW()-INTERVAL 30 MINUTE, 0),
(UUID(),  8, NOW()-INTERVAL 1 DAY,    NOW()-INTERVAL 1 DAY-INTERVAL 1 HOUR, 0),
(UUID(),  9, NOW()-INTERVAL 1 DAY,    NOW()-INTERVAL 1 DAY-INTERVAL 1 HOUR, 1),
(UUID(), 10, NOW()+INTERVAL 2 HOUR,   NOW()-INTERVAL 1 HOUR, 0),
(UUID(), 11, NOW()-INTERVAL 3 DAY,    NOW()-INTERVAL 3 DAY-INTERVAL 1 HOUR, 0),
(UUID(), 12, NOW()-INTERVAL 3 DAY,    NOW()-INTERVAL 3 DAY-INTERVAL 1 HOUR, 1),
(UUID(), 13, NOW()+INTERVAL 45 MINUTE,NOW()-INTERVAL 15 MINUTE, 0),
(UUID(), 14, NOW()-INTERVAL 2 DAY,    NOW()-INTERVAL 2 DAY-INTERVAL 1 HOUR, 0),
(UUID(), 15, NOW()-INTERVAL 2 DAY,    NOW()-INTERVAL 2 DAY-INTERVAL 1 HOUR, 1),
(UUID(), 16, NOW()+INTERVAL 1 HOUR,   NOW(), 0),
(UUID(), 17, NOW()-INTERVAL 4 DAY,    NOW()-INTERVAL 4 DAY-INTERVAL 1 HOUR, 0),
(UUID(), 18, NOW()-INTERVAL 4 DAY,    NOW()-INTERVAL 4 DAY-INTERVAL 1 HOUR, 1),
(UUID(), 19, NOW()+INTERVAL 20 MINUTE,NOW()-INTERVAL 40 MINUTE, 0),
(UUID(), 20, NOW()-INTERVAL 6 DAY,    NOW()-INTERVAL 6 DAY-INTERVAL 1 HOUR, 0);

-- ============================================================
-- 7. UNITS (20)
-- ============================================================
INSERT INTO units (token, name, abbreviation, description, quantity, created_at, created_by) VALUES
(UUID(), 'KILOGRAMO',   'kg',   'UNIDAD DE MASA ESTÁNDAR',                         0, NOW(), 1),
(UUID(), 'GRAMO',       'g',    'FRACCIÓN DEL KILOGRAMO',                           0, NOW(), 1),
(UUID(), 'LIBRA',       'lb',   'UNIDAD DE MASA ANGLOSAJONA APROX 453 G',           0, NOW(), 1),
(UUID(), 'LITRO',       'L',    'UNIDAD DE VOLUMEN ESTÁNDAR',                       0, NOW(), 1),
(UUID(), 'MILILITRO',   'ml',   'FRACCIÓN DEL LITRO',                               0, NOW(), 1),
(UUID(), 'TAZA',        'tza',  'MEDIDA DE COCINA APROX 240 ML',                    0, NOW(), 1),
(UUID(), 'CUCHARADA',   'cda',  'MEDIDA DE COCINA APROX 15 ML',                     0, NOW(), 1),
(UUID(), 'CUCHARADITA', 'cdta', 'MEDIDA DE COCINA APROX 5 ML',                      0, NOW(), 1),
(UUID(), 'UNIDAD',      'und',  'PIEZAS INDIVIDUALES CONTABLES',                    0, NOW(), 1),
(UUID(), 'DOCENA',      'doc',  'GRUPO DE 12 UNIDADES',                             0, NOW(), 1),
(UUID(), 'PAQUETE',     'paq',  'EMPAQUE COMERCIAL CERRADO',                        0, NOW(), 1),
(UUID(), 'BOLSA',       'bol',  'BOLSA DE PRESENTACIÓN VARIABLE',                   0, NOW(), 1),
(UUID(), 'CAJA',        'caj',  'CAJA DE CARTÓN O PLÁSTICO',                        0, NOW(), 1),
(UUID(), 'GALÓN',       'gal',  'UNIDAD DE VOLUMEN APROX 3785 ML',                  0, NOW(), 1),
(UUID(), 'ONZA',        'oz',   'UNIDAD DE MASA APROX 28 G',                        0, NOW(), 1),
(UUID(), 'METRO',       'm',    'UNIDAD DE LONGITUD PARA PAPEL PARAFINADO ETC',     0, NOW(), 1),
(UUID(), 'CENTÍMETRO',  'cm',   'FRACCIÓN DEL METRO',                               0, NOW(), 1),
(UUID(), 'PORCIÓN',     'por',  'RACIÓN ESTÁNDAR DE SERVICIO',                      0, NOW(), 1),
(UUID(), 'BANDEJA',     'bdj',  'BANDEJA DE HORNEADO CAPACIDAD VARIABLE',           0, NOW(), 1),
(UUID(), 'LATA',        'lta',  'LATA DE CONSERVAS O INGREDIENTE ENVASADO',         0, NOW(), 1);

-- ============================================================
-- 8. SUPPLY_CATEGORIES (20)
-- ============================================================
INSERT INTO supply_categories (token, name, description, status, created_at, created_by) VALUES
(UUID(), 'HARINAS Y ALMIDONES',    'HARINAS DE TRIGO, MAÍZ, ARROZ Y ALMIDONES VARIOS',          'active', NOW(), 1),
(UUID(), 'AZÚCARES Y ENDULZANTES', 'AZÚCAR BLANCA, MORENA, PANELA, MIEL Y EDULCORANTES',        'active', NOW(), 1),
(UUID(), 'GRASAS Y ACEITES',       'MANTEQUILLA, MARGARINA, ACEITE VEGETAL Y MANTECA',           'active', NOW(), 1),
(UUID(), 'LÁCTEOS',                'LECHE, CREMA DE LECHE, QUESO, YOGUR Y DERIVADOS',            'active', NOW(), 1),
(UUID(), 'HUEVOS',                 'HUEVOS FRESCOS DE GALLINA Y OTRAS AVES',                     'active', NOW(), 1),
(UUID(), 'LEVADURAS Y LEUDANTES',  'LEVADURA FRESCA, SECA, POLVO DE HORNEAR Y BICARBONATO',      'active', NOW(), 1),
(UUID(), 'SAL Y CONDIMENTOS',      'SAL DE MESA, SAL MARINA, ESPECIAS Y CONDIMENTOS',            'active', NOW(), 1),
(UUID(), 'CHOCOLATES Y CACAO',     'CACAO EN POLVO, COBERTURA, CHIPS DE CHOCOLATE',              'active', NOW(), 1),
(UUID(), 'FRUTAS Y PULPAS',        'FRUTAS FRESCAS, PULPAS CONGELADAS Y DESHIDRATADAS',          'active', NOW(), 1),
(UUID(), 'ESENCIAS Y COLORANTES',  'VAINILLA, ESENCIAS ARTIFICIALES Y COLORANTES ALIMENTARIOS',  'active', NOW(), 1),
(UUID(), 'FRUTOS SECOS',           'NUECES, ALMENDRAS, MANÍ, UVAS PASAS Y SIMILARES',            'active', NOW(), 1),
(UUID(), 'SEMILLAS',               'AJONJOLÍ, GIRASOL, LINAZA, AMAPOLA Y OTRAS SEMILLAS',        'active', NOW(), 1),
(UUID(), 'RELLENOS Y MERMELADAS',  'AREQUIPE, MERMELADAS, CREMAS PASTELERAS Y JALEAS',           'active', NOW(), 1),
(UUID(), 'DECORACIONES',           'FONDANT, GLASEADOS, PERLAS, GRAGEAS Y DECORACIONES',         'active', NOW(), 1),
(UUID(), 'EMPAQUES',               'BOLSAS, CAJAS, PAPEL PARAFINADO Y ENVOLTURAS',               'active', NOW(), 1),
(UUID(), 'BEBIDAS Y LÍQUIDOS',     'AGUA, JUGOS, LECHE VEGETAL Y LÍQUIDOS PARA RECETAS',         'active', NOW(), 1),
(UUID(), 'ADITIVOS',               'MEJORADORES DE PAN, EMULSIFICANTES Y CONSERVANTES',          'active', NOW(), 1),
(UUID(), 'COBERTURAS',             'BETÚN, GANACHE, GLASEADO ESPEJO Y COBERTURAS VARIAS',        'active', NOW(), 1),
(UUID(), 'PROTEÍNAS',              'CARNES FRÍAS, JAMÓN Y PROTEÍNAS PARA RELLENOS SALADOS',      'active', NOW(), 1),
(UUID(), 'VARIOS / MISCELÁNEOS',   'INSUMOS QUE NO ENCAJAN EN CATEGORÍAS ANTERIORES',            'active', NOW(), 1);

-- ============================================================
-- 9. SUPPLIES (20)
-- ============================================================
INSERT INTO supplies (token, name, description, category_id, unit_id,
                      available_quantity, min_stock, max_stock,
                      status, created_at, created_by) VALUES
(UUID(), 'HARINA DE TRIGO TODO USO',  'HARINA BLANCA MULTIPROPÓSITO PARA PAN Y REPOSTERÍA', 1, 1,  50.0, 10.0, 100.0, 'active', NOW(), 1),
(UUID(), 'HARINA DE MAÍZ AMARILLA',   'HARINA DE MAÍZ PARA AREPAS Y MASAS REGIONALES',      1, 1,  20.0,  5.0,  50.0, 'active', NOW(), 1),
(UUID(), 'AZÚCAR BLANCA REFINADA',    'AZÚCAR GRANULADA ESTÁNDAR',                           2, 1,  30.0,  5.0,  80.0, 'active', NOW(), 1),
(UUID(), 'PANELA EN BLOQUE',          'PANELA ENTERA DE CAÑA COLOMBIANA',                    2, 9,  40.0, 10.0, 100.0, 'active', NOW(), 1),
(UUID(), 'MANTEQUILLA SIN SAL',       'MANTEQUILLA DE VACA SIN SAL PARA REPOSTERÍA',         3, 1,  15.0,  3.0,  40.0, 'active', NOW(), 1),
(UUID(), 'ACEITE VEGETAL',            'ACEITE DE PALMA O GIRASOL PARA FRITURAS Y MASAS',     3, 4,  10.0,  2.0,  30.0, 'active', NOW(), 1),
(UUID(), 'LECHE ENTERA PASTEURIZADA', 'LECHE LÍQUIDA ENTERA EN BOLSA O CAJA',                4, 4,  20.0,  5.0,  60.0, 'active', NOW(), 1),
(UUID(), 'CREMA DE LECHE',            'CREMA DE LECHE 30% DE GRASA PARA RELLENOS',           4, 4,   8.0,  2.0,  20.0, 'active', NOW(), 1),
(UUID(), 'HUEVOS FRESCOS AA',         'HUEVOS DE GALLINA TAMAÑO AA',                         5, 9, 120.0, 30.0, 300.0, 'active', NOW(), 1),
(UUID(), 'LEVADURA SECA INSTANTÁNEA', 'LEVADURA GRANULADA DE ACCIÓN RÁPIDA',                 6, 2, 500.0,100.0,2000.0, 'active', NOW(), 1),
(UUID(), 'POLVO DE HORNEAR',          'LEUDANTE QUÍMICO DOBLE ACCIÓN',                       6, 2, 300.0, 50.0,1000.0, 'active', NOW(), 1),
(UUID(), 'SAL REFINADA',              'SAL DE MESA YODADA',                                  7, 1,  10.0,  2.0,  25.0, 'active', NOW(), 1),
(UUID(), 'CACAO EN POLVO SIN AZÚCAR', 'CACAO 100% NATURAL PARA REPOSTERÍA',                  8, 2, 200.0, 50.0, 800.0, 'active', NOW(), 1),
(UUID(), 'CHIPS DE CHOCOLATE OSCURO', 'TROCITOS DE COBERTURA DE CHOCOLATE 60% CACAO',        8, 2, 150.0, 30.0, 500.0, 'active', NOW(), 1),
(UUID(), 'ESENCIA DE VAINILLA',       'EXTRACTO NATURAL DE VAINILLA',                       10, 5,   2.0,  0.5,   5.0, 'active', NOW(), 1),
(UUID(), 'AREQUIPE INDUSTRIAL',       'AREQUIPE EN CUBETA PARA RELLENOS Y DECORACIÓN',      13, 1,  12.0,  3.0,  30.0, 'active', NOW(), 1),
(UUID(), 'NUECES PELADAS',            'NUECES ENTERAS SIN CÁSCARA PARA PONQUÉS',            11, 2, 500.0,100.0,2000.0, 'active', NOW(), 1),
(UUID(), 'AJONJOLÍ TOSTADO',          'SEMILLAS DE SÉSAMO TOSTADAS PARA CUBIERTA DE PAN',  12, 2, 300.0, 50.0,1000.0, 'active', NOW(), 1),
(UUID(), 'FONDANT BLANCO',            'FONDANT LISTO PARA USO EN DECORACIÓN DE TORTAS',     14, 1,   5.0,  1.0,  15.0, 'active', NOW(), 1),
(UUID(), 'COLORANTE ROJO CARMÍN',     'COLORANTE ALIMENTARIO EN GEL COLOR ROJO',            10, 5,   0.5,  0.1,   2.0, 'active', NOW(), 1);

-- ============================================================
-- 10. PRODUCTS (20)
-- ============================================================
INSERT INTO products (token, name, description, unit_id,
                      available_quantity, min_stock, max_stock,
                      is_locked, status, created_at, created_by) VALUES
(UUID(), 'PAN FRANCÉS',           'PAN BLANCO DE CORTEZA CRUJIENTE 80 G',                9,  50.0, 20.0, 200.0, 0, 'active', NOW(), 1),
(UUID(), 'ALMOJÁBANA',            'PANDEYUCA DE QUESO ESPECIALIDAD COLOMBIANA',           9,  24.0, 12.0, 120.0, 0, 'active', NOW(), 1),
(UUID(), 'CROISSANT MANTEQUILLA', 'CROISSANT HOJALDRADO DE MANTEQUILLA 60 G',             9,  20.0, 10.0, 100.0, 0, 'active', NOW(), 1),
(UUID(), 'PONQUÉ MÁRMOL',         'TORTA MÁRMOL VAINILLA-CHOCOLATE MOLDE MEDIANO',        9,   5.0,  2.0,  20.0, 0, 'active', NOW(), 1),
(UUID(), 'TORTA DE TRES LECHES',  'BIZCOCHO BAÑADO EN TRES LECHES 25 PORCIONES',          18,  3.0,  1.0,  10.0, 0, 'active', NOW(), 1),
(UUID(), 'ROSCÓN DE GUAYABA',     'ROSCÓN RELLENO DE BOCADILLO DE GUAYABA',               9,  12.0,  6.0,  60.0, 0, 'active', NOW(), 1),
(UUID(), 'GALLETA DE CHIPS',      'GALLETA AMERICANA CON CHIPS DE CHOCOLATE 50 G',        9,  48.0, 24.0, 240.0, 0, 'active', NOW(), 1),
(UUID(), 'MOGOLLA INTEGRAL',      'PAN INTEGRAL DE TRIGO CON SEMILLAS 70 G',              9,  30.0, 15.0, 150.0, 0, 'active', NOW(), 1),
(UUID(), 'BISCOCHO DE MAÍZ',      'BISCOCHO ESPONJOSO DE HARINA DE MAÍZ',                9,  40.0, 20.0, 200.0, 0, 'active', NOW(), 1),
(UUID(), 'PALITO DE QUESO',       'PALITO CRUJIENTE DE QUESO RALLADO 40 G',               9,  60.0, 30.0, 300.0, 0, 'active', NOW(), 1),
(UUID(), 'CUERNITO DE AREQUIPE',  'PAN CON FORMA DE CUERNO RELLENO DE AREQUIPE',          9,  24.0, 12.0, 120.0, 0, 'active', NOW(), 1),
(UUID(), 'PAN DE BONO',           'PAN DE QUESO Y ALMIDÓN DE YUCA 40 G',                 9,  30.0, 24.0, 240.0, 0, 'active', NOW(), 1),
(UUID(), 'MUFFIN DE VAINILLA',    'MUFFIN ESPONJOSO DE VAINILLA CON TOPPING DE AZÚCAR',  9,  12.0, 12.0, 120.0, 0, 'active', NOW(), 1),
(UUID(), 'BROWNIE DE CHOCOLATE',  'BROWNIE HÚMEDO DE CHOCOLATE AMARGO 80 G',              9,  20.0, 12.0, 120.0, 0, 'active', NOW(), 1),
(UUID(), 'TORTA RED VELVET',      'TORTA TERCIOPELO ROJO CON FROSTING DE QUESO CREMA',   18,   2.0,  1.0,  10.0, 0, 'active', NOW(), 1),
(UUID(), 'ÑAPA / ADICIÓN',        'PIEZA ADICIONAL DE CORTESÍA AL CLIENTE',               9,   0.0,  0.0,   0.0, 1, 'active', NOW(), 1),
(UUID(), 'ÉCLAIR DE CREMA',       'MASA CHOUX RELLENA DE CREMA PASTELERA Y GLASEADA',    9,  12.0,  8.0,  80.0, 0, 'active', NOW(), 1),
(UUID(), 'PAN DE YUCA',           'PAN TRADICIONAL DE ALMIDÓN DE YUCA Y QUESO BLANCO',   9,  36.0, 20.0, 200.0, 0, 'active', NOW(), 1),
(UUID(), 'TORTA DE CUMPLEAÑOS',   'TORTA PERSONALIZADA A PEDIDO 30 PORCIONES',            18,  1.0,  0.0,   5.0, 0, 'active', NOW(), 1),
(UUID(), 'EMPANADA DE PIPIÁN',    'EMPANADA DE MAÍZ RELLENA DE PAPA CON HOGAO Y PIPIÁN', 9,  24.0, 10.0, 100.0, 0, 'active', NOW(), 1);

-- ============================================================
-- 11. RECIPES (20)
-- ============================================================
INSERT INTO recipes (token, name, description, product_id, yield_quantity, yield_unit_id,
                     status, created_at, created_by) VALUES
(UUID(), 'RECETA PAN FRANCÉS',          'MASA BÁSICA DE PAN BLANCO PARA HORNEAR',                   1,  80.0, 9, 'active', NOW(), 3),
(UUID(), 'RECETA ALMOJÁBANA',           'MEZCLA DE QUESO, HUEVO Y HARINA DE MAÍZ',                  2,  24.0, 9, 'active', NOW(), 3),
(UUID(), 'RECETA CROISSANT',            'MASA HOJALDRADA CON MANTEQUILLA DE ALTA CALIDAD',           3,  20.0, 9, 'active', NOW(), 3),
(UUID(), 'RECETA PONQUÉ MÁRMOL',        'BIZCOCHO DE VAINILLA Y CHOCOLATE ENTRELAZADO',              4,   1.0, 9, 'active', NOW(), 4),
(UUID(), 'RECETA TRES LECHES',          'BIZCOCHO ESPONJOSO BAÑADO EN MEZCLA DE TRES LÁCTEOS',       5,  25.0,18, 'active', NOW(), 4),
(UUID(), 'RECETA ROSCÓN GUAYABA',       'MASA ENRIQUECIDA RELLENA DE BOCADILLO',                     6,  12.0, 9, 'active', NOW(), 3),
(UUID(), 'RECETA GALLETA CHIPS',        'MASA DE MANTEQUILLA CON CHIPS DE CHOCOLATE',                7,  48.0, 9, 'active', NOW(), 4),
(UUID(), 'RECETA MOGOLLA INTEGRAL',     'PAN INTEGRAL CON SEMILLAS DE AJONJOLÍ Y LINAZA',            8,  30.0, 9, 'active', NOW(), 3),
(UUID(), 'RECETA BISCOCHO MAÍZ',        'BISCOCHO ESPONJOSO DE HARINA DE MAÍZ Y PANELA',             9,  40.0, 9, 'active', NOW(), 3),
(UUID(), 'RECETA PALITO DE QUESO',      'MASA CRUJIENTE DE QUESO EXTRUIDO Y HORNEADO',              10,  60.0, 9, 'active', NOW(), 3),
(UUID(), 'RECETA CUERNITO AREQUIPE',    'PAN DULCE RELLENO DE AREQUIPE COLOMBIANO',                 11,  24.0, 9, 'active', NOW(), 3),
(UUID(), 'RECETA PAN DE BONO',          'PAN DE ALMIDÓN DE YUCA Y QUESO COSTEÑO',                   12,  30.0, 9, 'active', NOW(), 3),
(UUID(), 'RECETA MUFFIN VAINILLA',      'CUPCAKE ESPONJOSO DE VAINILLA CON TOPPING',                13,  12.0, 9, 'active', NOW(), 4),
(UUID(), 'RECETA BROWNIE CHOCOLATE',    'BROWNIE DENSO DE CHOCOLATE Y MANTEQUILLA',                  14,  20.0, 9, 'active', NOW(), 4),
(UUID(), 'RECETA RED VELVET',           'TORTA DE CACAO Y COLORANTE ROJO CON FROSTING',             15,   1.0, 9, 'active', NOW(), 4),
(UUID(), 'RECETA ÉCLAIR CREMA',         'MASA CHOUX Y CREMA PASTELERA DE VAINILLA',                 17,  12.0, 9, 'active', NOW(), 4),
(UUID(), 'RECETA PAN DE YUCA',          'MEZCLA DE ALMIDÓN DE YUCA Y QUESO BLANCO',                 18,  36.0, 9, 'active', NOW(), 3),
(UUID(), 'RECETA EMPANADA PIPIÁN',      'MASA DE MAÍZ RELLENA CON PAPA Y HOGAO',                    20,  24.0, 9, 'active', NOW(), 3),
(UUID(), 'RECETA BASE BIZCOCHO',        'BIZCOCHO NEUTRO REUTILIZABLE PARA TORTAS DE ENCARGO',     NULL,  1.0, 9, 'active', NOW(), 4),
(UUID(), 'RECETA MASA HOJALDRADA BASE', 'MASA HOJALDRADA GENÉRICA PARA DERIVADOS VARIOS',          NULL,  1.0, 1, 'active', NOW(), 3);

-- ============================================================
-- 12. RECIPE_INGREDIENTS (20)
-- ============================================================
INSERT INTO recipe_ingredients (token, recipe_id, supply_id, quantity, unit_id, notes) VALUES
(UUID(), 1,  1, 1.000, 1, 'HARINA TODO USO CERNIDA'),
(UUID(), 1, 10, 7.000, 2, 'LEVADURA SECA INSTANTÁNEA'),
(UUID(), 1, 12, 0.020, 1, 'SAL REFINADA'),
(UUID(), 1,  7, 0.600, 4, 'AGUA TIBIA NO CALIENTE'),
(UUID(), 2,  2, 0.500, 1, 'HARINA DE MAÍZ AMARILLA'),
(UUID(), 2,  9, 2.000, 9, 'HUEVOS FRESCOS AA'),
(UUID(), 2, 12, 0.010, 1, 'PIZCA DE SAL'),
(UUID(), 3,  1, 0.500, 1, 'HARINA DE TRIGO'),
(UUID(), 3,  5, 0.250, 1, 'MANTEQUILLA SIN SAL FRÍA EN CAPAS'),
(UUID(), 3,  7, 0.120, 4, 'LECHE ENTERA'),
(UUID(), 4,  1, 0.300, 1, 'HARINA DE TRIGO'),
(UUID(), 4,  3, 0.250, 1, 'AZÚCAR BLANCA'),
(UUID(), 4,  5, 0.200, 1, 'MANTEQUILLA SIN SAL'),
(UUID(), 4,  9, 3.000, 9, 'HUEVOS FRESCOS'),
(UUID(), 4, 13, 0.050, 2, 'CACAO EN POLVO PARA PARTE OSCURA'),
(UUID(), 7,  1, 0.280, 1, 'HARINA TODO USO'),
(UUID(), 7,  3, 0.200, 1, 'AZÚCAR BLANCA'),
(UUID(), 7,  5, 0.150, 1, 'MANTEQUILLA SIN SAL'),
(UUID(), 7, 14, 0.100, 2, 'CHIPS DE CHOCOLATE OSCURO'),
(UUID(), 7, 15, 0.005, 5, 'ESENCIA DE VAINILLA');

-- ============================================================
-- 13. PRODUCTION_ORDERS (20)
-- Modelo actualizado: started_at, cancelled_at
-- ============================================================
INSERT INTO production_orders (token, recipe_id, quantity_multiplier, total_yield,
                                status, scheduled_at, started_at, completed_at, cancelled_at,
                                notes, created_at, created_by) VALUES
(UUID(),  1, 2.0, 160.0, 'completed',  NOW()-INTERVAL 5 DAY, NOW()-INTERVAL 5 DAY+INTERVAL 1 HOUR, NOW()-INTERVAL 5 DAY+INTERVAL 3 HOUR, NULL, 'LOTE MATUTINO DOBLE',              NOW()-INTERVAL 5 DAY, 3),
(UUID(),  2, 1.0,  24.0, 'completed',  NOW()-INTERVAL 4 DAY, NOW()-INTERVAL 4 DAY+INTERVAL 1 HOUR, NOW()-INTERVAL 4 DAY+INTERVAL 2 HOUR, NULL, 'PRODUCCIÓN REGULAR',               NOW()-INTERVAL 4 DAY, 3),
(UUID(),  3, 1.5,  30.0, 'completed',  NOW()-INTERVAL 3 DAY, NOW()-INTERVAL 3 DAY+INTERVAL 1 HOUR, NOW()-INTERVAL 3 DAY+INTERVAL 4 HOUR, NULL, 'PEDIDO ESPECIAL',                  NOW()-INTERVAL 3 DAY, 3),
(UUID(),  4, 1.0,   1.0, 'completed',  NOW()-INTERVAL 2 DAY, NOW()-INTERVAL 2 DAY+INTERVAL 1 HOUR, NOW()-INTERVAL 2 DAY+INTERVAL 2 HOUR, NULL, 'TORTA VITRINA',                    NOW()-INTERVAL 2 DAY, 4),
(UUID(),  5, 2.0,  50.0, 'completed',  NOW()-INTERVAL 1 DAY, NOW()-INTERVAL 1 DAY+INTERVAL 1 HOUR, NOW()-INTERVAL 1 DAY+INTERVAL 3 HOUR, NULL, 'EVENTO EMPRESARIAL',               NOW()-INTERVAL 1 DAY, 4),
(UUID(),  7, 3.0, 144.0, 'completed',  NOW()-INTERVAL 1 DAY, NOW()-INTERVAL 1 DAY+INTERVAL 30 MINUTE, NOW()-INTERVAL 1 DAY+INTERVAL 1 HOUR, NULL, 'GALLETAS A GRANEL',             NOW()-INTERVAL 1 DAY, 4),
(UUID(),  1, 1.0,  80.0, 'in_progress',NOW(),                 NOW(),                                NULL,                                   NULL, 'TURNO TARDE',                      NOW(), 3),
(UUID(),  8, 1.0,  30.0, 'in_progress',NOW(),                 NOW(),                                NULL,                                   NULL, 'PAN INTEGRAL SEMANA',              NOW(), 3),
(UUID(),  9, 2.0,  80.0, 'pending',    NOW()+INTERVAL 1 DAY,  NULL,                                 NULL,                                   NULL, 'MARTES BISCOCHO',                  NOW(), 3),
(UUID(), 10, 2.0, 120.0, 'pending',    NOW()+INTERVAL 1 DAY,  NULL,                                 NULL,                                   NULL, 'PALITOS PARA EVENTO',              NOW(), 3),
(UUID(), 11, 1.0,  24.0, 'pending',    NOW()+INTERVAL 2 DAY,  NULL,                                 NULL,                                   NULL, 'CUERNITOS MIÉRCOLES',              NOW(), 3),
(UUID(), 12, 1.5,  45.0, 'pending',    NOW()+INTERVAL 2 DAY,  NULL,                                 NULL,                                   NULL, 'PAN BONO X45',                     NOW(), 3),
(UUID(), 13, 2.0,  24.0, 'pending',    NOW()+INTERVAL 3 DAY,  NULL,                                 NULL,                                   NULL, 'MUFFINS JUEVES',                   NOW(), 4),
(UUID(), 14, 1.0,  20.0, 'pending',    NOW()+INTERVAL 3 DAY,  NULL,                                 NULL,                                   NULL, 'BROWNIES JUEVES',                  NOW(), 4),
(UUID(), 15, 1.0,   1.0, 'pending',    NOW()+INTERVAL 4 DAY,  NULL,                                 NULL,                                   NULL, 'TORTA ENCARGO',                    NOW(), 4),
(UUID(), 16, 2.0,  24.0, 'pending',    NOW()+INTERVAL 4 DAY,  NULL,                                 NULL,                                   NULL, 'ÉCLAIRS VIERNES',                  NOW(), 4),
(UUID(), 17, 3.0, 108.0, 'pending',    NOW()+INTERVAL 5 DAY,  NULL,                                 NULL,                                   NULL, 'PAN YUCA SEMANA',                  NOW(), 3),
(UUID(), 18, 2.0,  48.0, 'pending',    NOW()+INTERVAL 5 DAY,  NULL,                                 NULL,                                   NULL, 'EMPANADAS SÁBADO',                 NOW(), 3),
(UUID(),  6, 1.0,  12.0, 'cancelled',  NOW()-INTERVAL 6 DAY,  NULL,                                 NULL,                                   NOW()-INTERVAL 6 DAY+INTERVAL 2 HOUR, 'CANCELADO POR FALTA DE BOCADILLO', NOW()-INTERVAL 6 DAY, 3),
(UUID(),  4, 1.0,   1.0, 'cancelled',  NOW()-INTERVAL 7 DAY,  NULL,                                 NULL,                                   NOW()-INTERVAL 7 DAY+INTERVAL 1 HOUR, 'CLIENTE CANCELÓ PEDIDO ANTICIPADO',NOW()-INTERVAL 7 DAY, 4);

-- ============================================================
-- 14. PRODUCTION_ORDER_SNAPSHOTS (20)
-- ============================================================
INSERT INTO production_order_snapshots (token, production_order_id, supply_id,
                                         quantity_used, unit_id, stock_before, stock_after) VALUES
(UUID(), 1,  1, 2.000, 1,  52.0,   50.0),
(UUID(), 1, 10,14.000, 2, 514.0,  500.0),
(UUID(), 1, 12, 0.040, 1,  10.04,  10.0),
(UUID(), 2,  2, 0.500, 1,  20.5,   20.0),
(UUID(), 2,  9, 2.000, 9, 122.0,  120.0),
(UUID(), 3,  1, 0.750, 1,  50.75,  50.0),
(UUID(), 3,  5, 0.375, 1,  15.375, 15.0),
(UUID(), 3,  7, 0.180, 4,  20.18,  20.0),
(UUID(), 4,  1, 0.300, 1,  50.30,  50.0),
(UUID(), 4,  3, 0.250, 1,  30.25,  30.0),
(UUID(), 4,  5, 0.200, 1,  15.20,  15.0),
(UUID(), 4,  9, 3.000, 9, 123.0,  120.0),
(UUID(), 5,  7, 0.480, 4,  20.48,  20.0),
(UUID(), 5,  8, 0.200, 4,   8.20,   8.0),
(UUID(), 5,  3, 0.400, 1,  30.40,  30.0),
(UUID(), 6,  1, 0.840, 1,  50.84,  50.0),
(UUID(), 6,  3, 0.600, 1,  30.60,  30.0),
(UUID(), 6,  5, 0.450, 1,  15.45,  15.0),
(UUID(), 6, 14, 0.300, 2, 150.30, 150.0),
(UUID(), 6, 15, 0.015, 5,   2.015,  2.0);

-- ============================================================
-- 15. PROVIDERS (20)
-- ============================================================
INSERT INTO providers (token, company, nit, email, status, created_at, created_by) VALUES
(UUID(), 'HARINERA DEL VALLE S.A.',         '800123456-1', 'ventas@harinera.com.co',       'active',   NOW(), 1),
(UUID(), 'LEVAPAN S.A.',                    '800234567-2', 'comercial@levapan.com',         'active',   NOW(), 1),
(UUID(), 'INDUSTRIAS LÁCTEAS ANDINAS',      '800345678-3', 'pedidos@lacteasandinas.co',     'active',   NOW(), 1),
(UUID(), 'HUEVOS LA MACARENA LTDA.',        '800456789-4', 'ventas@huevosmacarena.co',      'active',   NOW(), 1),
(UUID(), 'COMPAÑÍA NACIONAL DE CHOCOLATES', '800567890-5', 'distribuidores@chocolates.com', 'active',   NOW(), 1),
(UUID(), 'AZUCARES DEL CAUCA S.A.',         '800678901-6', 'ventas@azucarescauca.com',      'active',   NOW(), 1),
(UUID(), 'GRASAS Y ACEITES ANDINOS LTDA.',  '800789012-7', 'contacto@grasasandinas.co',     'active',   NOW(), 1),
(UUID(), 'FRUTAS Y PULPAS DEL CAMPO',       '800890123-8', 'info@pulpascampo.co',           'active',   NOW(), 1),
(UUID(), 'AREQUIPES DEL TOLIMA S.A.S.',     '800901234-9', 'pedidos@arequipestolima.co',    'active',   NOW(), 1),
(UUID(), 'FRUTOS SELECTOS COLOMBIA',        '801012345-0', 'ventas@frutosselectos.co',      'active',   NOW(), 1),
(UUID(), 'EMPAQUES Y SOLUCIONES S.A.S.',    '801123456-1', 'empaques@soluciones.co',        'active',   NOW(), 1),
(UUID(), 'DISTRIBUIDORA EL MOLINO',         '801234567-2', 'elmolino@molino.com.co',        'active',   NOW(), 1),
(UUID(), 'ADITIVOS ALIMENTARIOS LTDA.',     '801345678-3', 'aditivos@alimentos.co',         'active',   NOW(), 1),
(UUID(), 'COLORANTES NATURALES ANDINOS',    '801456789-4', 'info@colorantesandinos.co',     'active',   NOW(), 1),
(UUID(), 'SEMILLAS DEL PACÍFICO S.A.S.',    '801567890-5', 'semillas@pacifico.co',          'active',   NOW(), 1),
(UUID(), 'INSUMOS DE REPOSTERÍA EXPRESS',   '801678901-6', 'reposteria@express.co',         'active',   NOW(), 1),
(UUID(), 'PANELERA LA CABAÑA',              '801789012-7', 'ventas@paneleracabana.co',      'active',   NOW(), 1),
(UUID(), 'TODO EMPAQUES COLOMBIA',          '801890123-8', 'info@todoempaques.co',          'active',   NOW(), 1),
(UUID(), 'QUESOS Y DERIVADOS DEL NORTE',    '801901234-9', 'ventas@quesosdeltnorte.co',     'active',   NOW(), 1),
(UUID(), 'SAL DEL MAR COLOMBIANO S.A.',     '802012345-0', 'sal@saldmar.co',                'inactive', NOW(), 1);

-- ============================================================
-- 16. PROVIDER_CONTACTS (20)
-- ============================================================
INSERT INTO provider_contacts (token, provider_id, name, email, phone, notes, created_at, created_by) VALUES
(UUID(),  1, 'HERNÁN OSPINA',    'hector.ospina@harinera.com.co',  '3101110001', 'GERENTE COMERCIAL ZONA ANDINA',         NOW(), 1),
(UUID(),  2, 'CLAUDIA RESTREPO', 'c.restrepo@levapan.com',         '3101110002', 'EJECUTIVA DE CUENTAS PRINCIPALES',      NOW(), 1),
(UUID(),  3, 'JORGE ARIAS',      'j.arias@lacteasandinas.co',      '3101110003', 'ASESOR DE VENTAS REFRIGERADOS',         NOW(), 1),
(UUID(),  4, 'BEATRIZ SERNA',    'b.serna@huevosmacarena.co',      '3101110004', 'COORDINADORA DE DISTRIBUCIÓN',         NOW(), 1),
(UUID(),  5, 'CAMILO QUINTERO',  'c.quintero@chocolates.com',      '3101110005', 'REPRESENTANTE ZONA CENTRO',             NOW(), 1),
(UUID(),  6, 'ADRIANA PALOMINO', 'a.palomino@azucarescauca.com',   '3101110006', 'GERENTE DE VENTAS INSTITUCIONALES',     NOW(), 1),
(UUID(),  7, 'NELSON CANO',      'n.cano@grasasandinas.co',        '3101110007', 'TÉCNICO DE PRODUCTOS ESPECIALES',       NOW(), 1),
(UUID(),  8, 'SANDRA MOLINA',    's.molina@pulpascampo.co',        '3101110008', 'ASESORA DE PEDIDOS EN LÍNEA',           NOW(), 1),
(UUID(),  9, 'FELIPE GUTIÉRREZ', 'f.gutierrez@arequipestolima.co', '3101110009', 'DIRECTOR COMERCIAL REGIONAL',           NOW(), 1),
(UUID(), 10, 'VALENTINA RONDÓN', 'v.rondon@frutosselectos.co',     '3101110010', 'EJECUTIVA DE IMPORTACIONES',            NOW(), 1),
(UUID(), 11, 'MAURICIO SALCEDO', 'm.salcedo@soluciones.co',        '3101110011', 'ASESOR DE EMPAQUES A MEDIDA',           NOW(), 1),
(UUID(), 12, 'CATALINA MORENO',  'c.moreno@molino.com.co',         '3101110012', 'ADMINISTRADORA DE PEDIDOS',             NOW(), 1),
(UUID(), 13, 'JAIRO SUÁREZ',     'j.suarez@alimentos.co',          '3101110013', 'EXPERTO TÉCNICO EN ADITIVOS',           NOW(), 1),
(UUID(), 14, 'LILIANA PEÑA',     'l.pena@colorantesandinos.co',    '3101110014', 'ASESORA DE COLORIMETRÍA ALIMENTARIA',   NOW(), 1),
(UUID(), 15, 'ÓSCAR VERGARA',    'o.vergara@pacifico.co',          '3101110015', 'ASESOR DE SEMILLAS ORGÁNICAS',          NOW(), 1),
(UUID(), 16, 'DIANA CASTILLO',   'd.castillo@express.co',          '3101110016', 'REPRESENTANTE DE INSUMOS ESPECIALES',   NOW(), 1),
(UUID(), 17, 'GONZALO BELTRÁN',  'g.beltran@paneleracabana.co',    '3101110017', 'PROPIETARIO Y REPRESENTANTE LEGAL',     NOW(), 1),
(UUID(), 18, 'VERÓNICA MEDINA',  'v.medina@todoempaques.co',       '3101110018', 'JEFE DE VENTAS CORPORATIVAS',           NOW(), 1),
(UUID(), 19, 'RAMIRO ESTRADA',   'r.estrada@quesosdeltnorte.co',   '3101110019', 'SUPERVISOR DE CALIDAD Y DISTRIBUCIÓN',  NOW(), 1),
(UUID(), 20, 'PAOLA RÍOS',       'p.rios@saldmar.co',              '3101110020', 'CONTACTO INACTIVO PROVEEDOR SUSPENDIDO',NOW(), 1);

-- ============================================================
-- 17. PRODUCT_CATEGORIES (20)
-- ============================================================
INSERT INTO product_categories (token, name, description, status, created_at, created_by) VALUES
(UUID(), 'LÁCTEOS Y DERIVADOS',      'LECHE, QUESOS, YOGURES Y PRODUCTOS DERIVADOS DE LA LECHE',    'active', NOW(), 1),
(UUID(), 'BEBIDAS',                  'GASEOSAS, JUGOS, AGUAS Y BEBIDAS EN GENERAL',                  'active', NOW(), 1),
(UUID(), 'PANADERÍA Y REPOSTERÍA',   'PANES, TORTAS, GALLETAS Y PRODUCTOS DE HORNEADO',              'active', NOW(), 1),
(UUID(), 'CONFITERÍA',               'DULCES, CHOCOLATES, CARAMELOS Y GOLOSINAS',                    'active', NOW(), 1),
(UUID(), 'ENLATADOS Y CONSERVAS',    'PRODUCTOS ENVASADOS, CONSERVAS Y ALIMENTOS EN LATA',           'active', NOW(), 1),
(UUID(), 'CEREALES Y GRANOS',        'ARROZ, AVENA, GRANOLA Y PRODUCTOS DE CEREALES',                'active', NOW(), 1),
(UUID(), 'SNACKS Y PASABOCAS',       'PAPAS FRITAS, MAÍZ PIRA, MANÍ Y SNACKS VARIOS',               'active', NOW(), 1),
(UUID(), 'CONDIMENTOS Y SALSAS',     'KÉTCHUP, MAYONESA, MOSTAZA, SALSAS Y ADEREZOS',               'active', NOW(), 1),
(UUID(), 'ACEITES Y GRASAS',         'ACEITES DE COCINA, MANTEQUILLA Y GRASAS COMESTIBLES',          'active', NOW(), 1),
(UUID(), 'HARINAS Y MEZCLAS',        'HARINAS PREPARADAS, MEZCLAS PARA TORTA Y SIMILARES',           'active', NOW(), 1),
(UUID(), 'AZÚCARES Y ENDULZANTES',   'AZÚCAR, PANELA, MIEL Y ENDULZANTES COMERCIALES',              'active', NOW(), 1),
(UUID(), 'CAFÉ E INFUSIONES',        'CAFÉ, TÉ, AROMÁTICAS Y BEBIDAS CALIENTES',                    'active', NOW(), 1),
(UUID(), 'EMBUTIDOS Y CARNES FRÍAS', 'SALCHICHAS, JAMÓN, MORTADELA Y EMBUTIDOS VARIOS',             'active', NOW(), 1),
(UUID(), 'HUEVOS',                   'HUEVOS DE GALLINA Y OTRAS AVES EN PRESENTACIONES COMERCIALES', 'active', NOW(), 1),
(UUID(), 'PRODUCTOS DE LIMPIEZA',    'JABONES, DETERGENTES Y PRODUCTOS DE ASEO PARA VENTA',         'active', NOW(), 1),
(UUID(), 'FRUTAS Y VERDURAS',        'FRUTAS FRESCAS, VERDURAS Y HORTALIZAS',                        'active', NOW(), 1),
(UUID(), 'CONGELADOS',               'PRODUCTOS CONGELADOS, HELADOS Y REFRIGERADOS',                 'active', NOW(), 1),
(UUID(), 'PASTAS Y FIDEOS',          'ESPAGUETI, MACARRÓN, LASAÑA Y PASTAS VARIAS',                 'active', NOW(), 1),
(UUID(), 'MISCELÁNEOS',              'PRODUCTOS QUE NO ENCAJAN EN OTRAS CATEGORÍAS',                 'active', NOW(), 1),
(UUID(), 'ARTÍCULOS DE CAFETERÍA',   'VASOS DESECHABLES, SERVILLETAS, PITILLOS Y SIMILARES',         'active', NOW(), 1);

-- ============================================================
-- 18. COMMERCIAL_PRODUCTS (20)
-- ============================================================
INSERT INTO commercial_products (token, name, description, category_id, unit_id,
                                  provider_id, purchase_price, sale_price,
                                  available_quantity, min_stock, max_stock,
                                  status, created_at, created_by) VALUES
(UUID(), 'LECHE ENTERA ALQUERÍA 1L',     'LECHE ENTERA PASTEURIZADA EN CAJA 1 LITRO',              1,  4,  3,  2800.0,  3500.0,  50.0, 10.0, 120.0, 'active', NOW(), 1),
(UUID(), 'COCA-COLA 400ML',              'GASEOSA COLA EN BOTELLA PLÁSTICA 400 ML',                 2,  9,  NULL, 1800.0,  2500.0, 120.0, 24.0, 300.0, 'active', NOW(), 1),
(UUID(), 'AGUA CRISTAL 600ML',           'AGUA PURIFICADA EN BOTELLA PLÁSTICA 600 ML',              2,  9,  NULL,  700.0,  1200.0, 100.0, 24.0, 240.0, 'active', NOW(), 1),
(UUID(), 'CHOCOLATE CORONA 500G',        'CHOCOLATE DE MESA EN PASTILLA 500 GRAMOS',                4, 11,  5,  8500.0, 12000.0,  30.0,  6.0,  80.0, 'active', NOW(), 1),
(UUID(), 'ATÚN EN LATA VAN CAMPS 160G',  'ATÚN EN AGUA EN LATA 160 GRAMOS',                        5, 20,  NULL, 3200.0,  4800.0,  60.0, 12.0, 150.0, 'active', NOW(), 1),
(UUID(), 'AVENA QUAKER 500G',            'AVENA EN HOJUELAS BOLSA 500 GRAMOS',                      6, 12,  NULL, 3500.0,  5200.0,  40.0,  8.0, 100.0, 'active', NOW(), 1),
(UUID(), 'PAPAS MARGARITA 105G',         'PAPAS FRITAS SABOR NATURAL BOLSA 105 GRAMOS',             7, 12,  NULL, 2200.0,  3200.0,  80.0, 20.0, 200.0, 'active', NOW(), 1),
(UUID(), 'KÉTCHUP FRUCO 400G',           'SALSA DE TOMATE EN BOLSA 400 GRAMOS',                     8, 12,  NULL, 3800.0,  5500.0,  35.0,  6.0,  90.0, 'active', NOW(), 1),
(UUID(), 'ACEITE OLEOCALI 1L',           'ACEITE VEGETAL DE GIRASOL BOTELLA 1 LITRO',               9,  4,  7,  8200.0, 11500.0,  25.0,  6.0,  70.0, 'active', NOW(), 1),
(UUID(), 'HARINA DE TRIGO HARINERA 1KG', 'HARINA DE TRIGO TODO USO BOLSA 1 KILOGRAMO',             10, 12,  1,  2400.0,  3600.0,  40.0, 10.0, 100.0, 'active', NOW(), 1),
(UUID(), 'AZÚCAR MANUELITA 1KG',         'AZÚCAR BLANCA REFINADA BOLSA 1 KILOGRAMO',               11, 12,  6,  2600.0,  3800.0,  50.0, 10.0, 120.0, 'active', NOW(), 1),
(UUID(), 'CAFÉ COLCAFÉ 250G',            'CAFÉ MOLIDO Y TOSTADO BOLSA 250 GRAMOS',                  12, 12,  NULL, 9500.0, 14000.0,  30.0,  6.0,  80.0, 'active', NOW(), 1),
(UUID(), 'SALCHICHÓN ZENÚ 500G',         'SALCHICHÓN CERVECERO EN EMPAQUE 500 GRAMOS',              13, 11,  NULL,12500.0, 18000.0,  20.0,  4.0,  60.0, 'active', NOW(), 1),
(UUID(), 'HUEVOS AA CODEGAN X12',        'CARTÓN DE 12 HUEVOS AA FRESCOS',                          14, 10,  4, 10500.0, 15000.0,  30.0,  6.0,  80.0, 'active', NOW(), 1),
(UUID(), 'JABÓN REY LAVAPLATOS 500G',    'JABÓN EN BARRA PARA LAVAR LOZA 500 GRAMOS',               15, 11,  NULL, 2800.0,  4200.0,  25.0,  5.0,  70.0, 'active', NOW(), 1),
(UUID(), 'MORA CONGELADA 500G',          'MORA DE CASTILLA CONGELADA BOLSA 500 GRAMOS',             17, 12,  8,  4500.0,  7000.0,  20.0,  4.0,  60.0, 'active', NOW(), 1),
(UUID(), 'ESPAGUETI DORIA 500G',         'PASTA ESPAGUETI BOLSA 500 GRAMOS',                        18, 12,  NULL, 2900.0,  4200.0,  40.0,  8.0, 100.0, 'active', NOW(), 1),
(UUID(), 'VASO DESECHABLE 7OZ X50',      'VASOS DESECHABLES TRANSPARENTES PAQUETE X50',             20, 11,  NULL, 3200.0,  5000.0,  30.0,  5.0,  80.0, 'active', NOW(), 1),
(UUID(), 'GRANOLA QUAKER 400G',          'GRANOLA CON FRUTAS Y MIEL BOLSA 400 GRAMOS',               6, 12,  NULL, 7500.0, 11000.0,  25.0,  5.0,  70.0, 'active', NOW(), 1),
(UUID(), 'YOGUR ALQUERÍA FRESA 200G',    'YOGUR BEBIBLE SABOR FRESA BOTELLA 200 GRAMOS',             1,  9,  3,  1800.0,  2800.0,  60.0, 12.0, 150.0, 'active', NOW(), 1);

-- ============================================================
-- 19. SALES (20)
-- status: 'COMPLETED' / 'ANNULLED'
-- user_id referencia users (cajeros/vendedores: ids 6,7,14)
-- ============================================================
INSERT INTO sales (token, user_id, sale_date, status, notes, created_at, created_by) VALUES
(UUID(),  6, NOW()-INTERVAL 6 DAY,  'COMPLETED', 'VENTA MATUTINA LUNES',             NOW()-INTERVAL 6 DAY,  6),
(UUID(),  7, NOW()-INTERVAL 6 DAY,  'COMPLETED', 'VENTA TARDE LUNES',                NOW()-INTERVAL 6 DAY,  7),
(UUID(),  6, NOW()-INTERVAL 5 DAY,  'COMPLETED', 'VENTA MARTES APERTURA',            NOW()-INTERVAL 5 DAY,  6),
(UUID(), 14, NOW()-INTERVAL 5 DAY,  'COMPLETED', 'PEDIDO EMPRESARIAL MARTES',        NOW()-INTERVAL 5 DAY, 14),
(UUID(),  7, NOW()-INTERVAL 4 DAY,  'COMPLETED', 'VENTA MIÉRCOLES',                  NOW()-INTERVAL 4 DAY,  7),
(UUID(),  6, NOW()-INTERVAL 4 DAY,  'ANNULLED',    'ANULADA POR ERROR EN CANTIDAD',    NOW()-INTERVAL 4 DAY,  6),
(UUID(), 14, NOW()-INTERVAL 3 DAY,  'COMPLETED', 'VENTA JUEVES MAÑANA',              NOW()-INTERVAL 3 DAY, 14),
(UUID(),  7, NOW()-INTERVAL 3 DAY,  'COMPLETED', 'PEDIDO DOMICILIO JUEVES',          NOW()-INTERVAL 3 DAY,  7),
(UUID(),  6, NOW()-INTERVAL 2 DAY,  'COMPLETED', 'VENTA VIERNES APERTURA',           NOW()-INTERVAL 2 DAY,  6),
(UUID(), 14, NOW()-INTERVAL 2 DAY,  'COMPLETED', 'VENTA VIERNES TARDE',              NOW()-INTERVAL 2 DAY, 14),
(UUID(),  7, NOW()-INTERVAL 2 DAY,  'ANNULLED',    'ANULADA POR PRODUCTO AGOTADO',     NOW()-INTERVAL 2 DAY,  7),
(UUID(),  6, NOW()-INTERVAL 1 DAY,  'COMPLETED', 'VENTA SÁBADO ALTA ROTACIÓN',       NOW()-INTERVAL 1 DAY,  6),
(UUID(), 14, NOW()-INTERVAL 1 DAY,  'COMPLETED', 'PEDIDO EVENTO SÁBADO',             NOW()-INTERVAL 1 DAY, 14),
(UUID(),  7, NOW()-INTERVAL 1 DAY,  'COMPLETED', 'VENTA SÁBADO TARDE',               NOW()-INTERVAL 1 DAY,  7),
(UUID(),  6, NOW()-INTERVAL 1 DAY,  'COMPLETED', 'VENTA SÁBADO CIERRE',              NOW()-INTERVAL 1 DAY,  6),
(UUID(), 14, NOW()-INTERVAL 12 HOUR,'COMPLETED', 'VENTA DOMINGO MAÑANA',             NOW()-INTERVAL 12 HOUR,14),
(UUID(),  7, NOW()-INTERVAL 10 HOUR,'COMPLETED', 'VENTA DOMINGO MEDIODÍA',           NOW()-INTERVAL 10 HOUR, 7),
(UUID(),  6, NOW()-INTERVAL 8 HOUR, 'COMPLETED', 'VENTA DOMINGO TARDE',              NOW()-INTERVAL 8 HOUR,  6),
(UUID(), 14, NOW()-INTERVAL 4 HOUR, 'COMPLETED', 'VENTA HOY MAÑANA',                 NOW()-INTERVAL 4 HOUR, 14),
(UUID(),  7, NOW()-INTERVAL 1 HOUR, 'COMPLETED', 'VENTA HOY RECIENTE',               NOW()-INTERVAL 1 HOUR,  7);

-- ============================================================
-- 20. SALE_ITEMS (20)
-- item_type: 'product' / 'commercial'
-- item_id referencia products o commercial_products según item_type
-- item_name guardado como snapshot del nombre al momento de venta
-- ============================================================
INSERT INTO sale_items (token, sale_id, item_type, item_id, item_name, quantity, created_at) VALUES
(UUID(),  1, 'product',    1, 'PAN FRANCÉS',              10.0, NOW()-INTERVAL 6 DAY),
(UUID(),  1, 'product',    7, 'GALLETA DE CHIPS',          6.0, NOW()-INTERVAL 6 DAY),
(UUID(),  2, 'commercial', 1, 'LECHE ENTERA ALQUERÍA 1L',  3.0, NOW()-INTERVAL 6 DAY),
(UUID(),  3, 'product',    2, 'ALMOJÁBANA',               12.0, NOW()-INTERVAL 5 DAY),
(UUID(),  3, 'commercial', 2, 'COCA-COLA 400ML',           4.0, NOW()-INTERVAL 5 DAY),
(UUID(),  4, 'product',    4, 'PONQUÉ MÁRMOL',             2.0, NOW()-INTERVAL 5 DAY),
(UUID(),  4, 'product',    5, 'TORTA DE TRES LECHES',      1.0, NOW()-INTERVAL 5 DAY),
(UUID(),  5, 'product',    3, 'CROISSANT MANTEQUILLA',     8.0, NOW()-INTERVAL 4 DAY),
(UUID(),  5, 'commercial', 4, 'CHOCOLATE CORONA 500G',     2.0, NOW()-INTERVAL 4 DAY),
(UUID(),  7, 'product',    8, 'MOGOLLA INTEGRAL',         15.0, NOW()-INTERVAL 3 DAY),
(UUID(),  7, 'product',   11, 'CUERNITO DE AREQUIPE',      6.0, NOW()-INTERVAL 3 DAY),
(UUID(),  8, 'commercial', 3, 'AGUA CRISTAL 600ML',        5.0, NOW()-INTERVAL 3 DAY),
(UUID(),  9, 'product',    1, 'PAN FRANCÉS',              20.0, NOW()-INTERVAL 2 DAY),
(UUID(),  9, 'product',   12, 'PAN DE BONO',              12.0, NOW()-INTERVAL 2 DAY),
(UUID(), 12, 'product',    9, 'BISCOCHO DE MAÍZ',         10.0, NOW()-INTERVAL 1 DAY),
(UUID(), 12, 'commercial', 7, 'PAPAS MARGARITA 105G',      8.0, NOW()-INTERVAL 1 DAY),
(UUID(), 13, 'product',   15, 'TORTA RED VELVET',          1.0, NOW()-INTERVAL 1 DAY),
(UUID(), 19, 'product',    1, 'PAN FRANCÉS',              15.0, NOW()-INTERVAL 4 HOUR),
(UUID(), 19, 'product',   13, 'MUFFIN DE VAINILLA',        6.0, NOW()-INTERVAL 4 HOUR),
(UUID(), 20, 'commercial', 2, 'COCA-COLA 400ML',           6.0, NOW()-INTERVAL 1 HOUR);

-- ============================================================
-- 21. INVENTORY_MOVEMENTS (20)
-- movement_type: 'sale' / 'sale_annulment'
-- item_type: 'product' / 'commercial'
-- reference_type: 'sale'
-- ============================================================
INSERT INTO inventory_movements (token, item_type, item_id, movement_type,
                                  quantity, stock_before, stock_after,
                                  reference_type, reference_id,
                                  user_id, created_at) VALUES
-- Venta 1: pan francés -10
(UUID(), 'product',     1, 'sale',          10.0,  60.0,  50.0, 'sale',  1,  6, NOW()-INTERVAL 6 DAY),
-- Venta 1: galleta chips -6
(UUID(), 'product',     7, 'sale',           6.0,  54.0,  48.0, 'sale',  1,  6, NOW()-INTERVAL 6 DAY),
-- Venta 2: leche alquería -3
(UUID(), 'commercial',  1, 'sale',           3.0,  53.0,  50.0, 'sale',  2,  7, NOW()-INTERVAL 6 DAY),
-- Venta 3: almojábana -12
(UUID(), 'product',     2, 'sale',          12.0,  36.0,  24.0, 'sale',  3,  6, NOW()-INTERVAL 5 DAY),
-- Venta 3: coca-cola -4
(UUID(), 'commercial',  2, 'sale',           4.0, 124.0, 120.0, 'sale',  3,  6, NOW()-INTERVAL 5 DAY),
-- Venta 4: ponqué mármol -2
(UUID(), 'product',     4, 'sale',           2.0,   7.0,   5.0, 'sale',  4, 14, NOW()-INTERVAL 5 DAY),
-- Venta 4: torta tres leches -1
(UUID(), 'product',     5, 'sale',           1.0,   4.0,   3.0, 'sale',  4, 14, NOW()-INTERVAL 5 DAY),
-- Venta 5: croissant -8
(UUID(), 'product',     3, 'sale',           8.0,  28.0,  20.0, 'sale',  5,  7, NOW()-INTERVAL 4 DAY),
-- Venta 5: chocolate corona -2
(UUID(), 'commercial',  4, 'sale',           2.0,  32.0,  30.0, 'sale',  5,  7, NOW()-INTERVAL 4 DAY),
-- Venta 6 ANULADA: reversa de pan francés +5
(UUID(), 'product',     1, 'sale_annulment', 5.0,  50.0,  55.0, 'sale',  6,  6, NOW()-INTERVAL 4 DAY),
-- Venta 7: mogolla integral -15
(UUID(), 'product',     8, 'sale',          15.0,  45.0,  30.0, 'sale',  7, 14, NOW()-INTERVAL 3 DAY),
-- Venta 7: cuernito arequipe -6
(UUID(), 'product',    11, 'sale',           6.0,  30.0,  24.0, 'sale',  7, 14, NOW()-INTERVAL 3 DAY),
-- Venta 8: agua cristal -5
(UUID(), 'commercial',  3, 'sale',           5.0, 105.0, 100.0, 'sale',  8,  7, NOW()-INTERVAL 3 DAY),
-- Venta 9: pan francés -20
(UUID(), 'product',     1, 'sale',          20.0,  55.0,  35.0, 'sale',  9,  6, NOW()-INTERVAL 2 DAY),
-- Venta 9: pan de bono -12
(UUID(), 'product',    12, 'sale',          12.0,  42.0,  30.0, 'sale',  9,  6, NOW()-INTERVAL 2 DAY),
-- Venta 11 ANULADA: reversa coca-cola +4
(UUID(), 'commercial',  2, 'sale_annulment', 4.0, 116.0, 120.0, 'sale', 11,  7, NOW()-INTERVAL 2 DAY),
-- Venta 12: biscocho de maíz -10
(UUID(), 'product',     9, 'sale',          10.0,  50.0,  40.0, 'sale', 12,  6, NOW()-INTERVAL 1 DAY),
-- Venta 13: torta red velvet -1
(UUID(), 'product',    15, 'sale',           1.0,   3.0,   2.0, 'sale', 13, 14, NOW()-INTERVAL 1 DAY),
-- Venta 19: pan francés -15
(UUID(), 'product',     1, 'sale',          15.0,  50.0,  35.0, 'sale', 19, 14, NOW()-INTERVAL 4 HOUR),
-- Venta 20: coca-cola -6
(UUID(), 'commercial',  2, 'sale',           6.0, 126.0, 120.0, 'sale', 20,  7, NOW()-INTERVAL 1 HOUR);

/*!40014 SET FOREIGN_KEY_CHECKS=1 */;

-- ============================================================
-- QUERIES DE VALIDACIÓN
-- ============================================================

-- Q01. Usuarios activos con su rol
SELECT u.id, CONCAT(u.first_name,' ',u.last_name) AS nombre,
       u.email, r.name AS rol, u.is_admin, u.status
FROM users u JOIN roles r ON u.role_id=r.id
WHERE u.deleted_at IS NULL ORDER BY u.id;

-- Q02. Ventas completadas con número de ítems
SELECT s.id, CONCAT(u.first_name,' ',u.last_name) AS vendedor,
       s.sale_date, s.status, COUNT(si.id) AS items,
       SUM(si.quantity) AS total_unidades, s.notes
FROM sales s
JOIN users u ON s.user_id=u.id
LEFT JOIN sale_items si ON si.sale_id=s.id
WHERE s.deleted_at IS NULL
GROUP BY s.id ORDER BY s.sale_date DESC;

-- Q03. Detalle de ítems por venta
SELECT s.id AS venta_id, s.sale_date, s.status,
       si.item_type, si.item_name, si.quantity
FROM sale_items si JOIN sales s ON si.sale_id=s.id
ORDER BY s.id, si.item_type;

-- Q04. Movimientos de inventario por tipo
SELECT im.item_type, im.item_id, im.movement_type,
       im.quantity, im.stock_before, im.stock_after,
       CONCAT(u.first_name,' ',u.last_name) AS usuario,
       im.created_at
FROM inventory_movements im JOIN users u ON im.user_id=u.id
ORDER BY im.created_at DESC;

-- Q05. Productos más vendidos (por cantidad)
SELECT si.item_name, si.item_type,
       SUM(si.quantity) AS total_vendido,
       COUNT(DISTINCT si.sale_id) AS num_ventas
FROM sale_items si
JOIN sales s ON si.sale_id=s.id
WHERE s.status='COMPLETED'
GROUP BY si.item_name, si.item_type
ORDER BY total_vendido DESC;

-- Q06. Ventas anuladas con su impacto revertido
SELECT s.id, s.sale_date,
       CONCAT(u.first_name,' ',u.last_name) AS vendedor,
       COUNT(si.id) AS items_anulados,
       SUM(si.quantity) AS unidades_devueltas
FROM sales s
JOIN users u ON s.user_id=u.id
LEFT JOIN sale_items si ON si.sale_id=s.id
WHERE s.status='ANNULLED'
GROUP BY s.id;

-- Q07. Insumos bajo mínimo
SELECT s.name AS insumo, sc.name AS categoria,
       u.abbreviation AS unidad,
       s.available_quantity AS stock, s.min_stock AS minimo,
       (s.min_stock - s.available_quantity) AS faltante
FROM supplies s
JOIN supply_categories sc ON s.category_id=sc.id
JOIN units u ON s.unit_id=u.id
WHERE s.available_quantity < s.min_stock AND s.deleted_at IS NULL
ORDER BY faltante DESC;

-- Q08. Órdenes de producción por estado
SELECT po.id, r.name AS receta, po.status,
       po.scheduled_at, po.started_at, po.completed_at, po.cancelled_at,
       po.total_yield, CONCAT(u.first_name,' ',u.last_name) AS creado_por
FROM production_orders po
JOIN recipes r ON po.recipe_id=r.id
JOIN users u ON po.created_by=u.id
WHERE po.deleted_at IS NULL ORDER BY po.scheduled_at DESC;

-- Q09. Productos comerciales con categoría y proveedor
SELECT cp.name AS producto, pc.name AS categoria,
       u.abbreviation AS unidad, pv.company AS proveedor,
       cp.purchase_price AS precio_compra,
       cp.sale_price AS precio_venta,
       cp.available_quantity AS stock, cp.status
FROM commercial_products cp
JOIN product_categories pc ON cp.category_id=pc.id
JOIN units u ON cp.unit_id=u.id
LEFT JOIN providers pv ON cp.provider_id=pv.id
WHERE cp.deleted_at IS NULL ORDER BY pc.name, cp.name;

-- Q10. Resumen ejecutivo general
SELECT
  (SELECT COUNT(*) FROM users           WHERE deleted_at IS NULL AND status='active')      AS usuarios_activos,
  (SELECT COUNT(*) FROM supplies        WHERE deleted_at IS NULL AND status='active')      AS insumos_activos,
  (SELECT COUNT(*) FROM products        WHERE deleted_at IS NULL AND status='active')      AS productos_activos,
  (SELECT COUNT(*) FROM commercial_products WHERE deleted_at IS NULL AND status='active')  AS prod_comerciales,
  (SELECT COUNT(*) FROM recipes         WHERE deleted_at IS NULL AND status='active')      AS recetas_activas,
  (SELECT COUNT(*) FROM production_orders WHERE deleted_at IS NULL AND status='pending')   AS ordenes_pendientes,
  (SELECT COUNT(*) FROM production_orders WHERE deleted_at IS NULL AND status='in_progress') AS en_produccion,
  (SELECT COUNT(*) FROM sales           WHERE deleted_at IS NULL AND status='COMPLETED')  AS ventas_completadas,
  (SELECT COUNT(*) FROM sales           WHERE deleted_at IS NULL AND status='ANNULLED')     AS ventas_anuladas,
  (SELECT COUNT(*) FROM providers       WHERE deleted_at IS NULL AND status='active')      AS proveedores_activos;

-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================

-- ============================================================
-- RESTAURAR USUARIO ADMIN POR DEFECTO
-- Necesario para poder entrar a la aplicación después del seed
-- Email: admin@saip.com | Password: admin123
-- ============================================================
UPDATE users
SET
    first_name    = 'Admin',
    last_name     = 'Sistema',
    email         = 'admin@saip.com',
    phone         = '0000000000',
    password_hash = '$2b$12$Uq/W1mm6vXUYiAIQVHd9EeJmOd8gUTkuvaCsMm4cLwwPlPQ194//W',
    is_admin      = 1,
    accepted_terms = 0,
    accepted_terms_at = NULL
WHERE id = 1;

-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================

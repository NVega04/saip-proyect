-- MySQL dump 10.13  Distrib 8.4.8, for Linux (x86_64)
--
-- Host: localhost    Database: db_saip_proyect
-- ------------------------------------------------------
-- Server version	8.4.8

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `categoria_productos`
--

DROP TABLE IF EXISTS `categoria_productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categoria_productos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `id_categoria_productos` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_categoria_padre` (`id_categoria_productos`),
  CONSTRAINT `fk_categoria_padre` FOREIGN KEY (`id_categoria_productos`) REFERENCES `productos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categoria_productos`
--

LOCK TABLES `categoria_productos` WRITE;
/*!40000 ALTER TABLE `categoria_productos` DISABLE KEYS */;
/*!40000 ALTER TABLE `categoria_productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categorias_insumos`
--

DROP TABLE IF EXISTS `categorias_insumos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias_insumos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `descripcion` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias_insumos`
--

LOCK TABLES `categorias_insumos` WRITE;
/*!40000 ALTER TABLE `categorias_insumos` DISABLE KEYS */;
/*!40000 ALTER TABLE `categorias_insumos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insumos`
--

DROP TABLE IF EXISTS `insumos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insumos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `id_categoria` int DEFAULT NULL,
  `descripcion` text,
  `cantidad_disponible` decimal(18,4) DEFAULT '0.0000',
  `stock_minimo` decimal(18,4) DEFAULT '0.0000',
  `stock_maximo` decimal(18,4) DEFAULT NULL,
  `id_proveedor` int DEFAULT NULL,
  `estado` enum('activo','inactivo') DEFAULT 'activo',
  `cantidad_producto` int DEFAULT NULL,
  `tipo_medida` varchar(50) DEFAULT NULL,
  `nombre_medida` varchar(50) DEFAULT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_insumo_categoria` (`id_categoria`),
  KEY `fk_insumo_proveedor` (`id_proveedor`),
  CONSTRAINT `fk_insumo_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `categorias_insumos` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_insumo_proveedor` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insumos`
--

LOCK TABLES `insumos` WRITE;
/*!40000 ALTER TABLE `insumos` DISABLE KEYS */;
/*!40000 ALTER TABLE `insumos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insumos_ordenes_compra`
--

DROP TABLE IF EXISTS `insumos_ordenes_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insumos_ordenes_compra` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `orden_compra` bigint NOT NULL,
  `item_type` enum('insumo','producto') NOT NULL,
  `item_id` int NOT NULL,
  `cantidad` decimal(18,4) NOT NULL,
  `precio_unitario` decimal(18,4) DEFAULT '0.0000',
  `subtotal` decimal(18,4) GENERATED ALWAYS AS ((`cantidad` * `precio_unitario`)) VIRTUAL,
  PRIMARY KEY (`id`),
  KEY `orden_compra` (`orden_compra`),
  CONSTRAINT `fk_poi_po` FOREIGN KEY (`orden_compra`) REFERENCES `insumos_ordenes_compra` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insumos_ordenes_compra`
--

LOCK TABLES `insumos_ordenes_compra` WRITE;
/*!40000 ALTER TABLE `insumos_ordenes_compra` DISABLE KEYS */;
/*!40000 ALTER TABLE `insumos_ordenes_compra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insumos_recetas`
--

DROP TABLE IF EXISTS `insumos_recetas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insumos_recetas` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `id_receta` bigint NOT NULL,
  `id_insumo` int NOT NULL,
  `cantidad` decimal(18,6) NOT NULL,
  `id_medida` int DEFAULT NULL,
  `porcentaje_perdida` decimal(5,2) DEFAULT '0.00',
  `orden` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `fk_ri_recipe` (`id_receta`),
  KEY `fk_ri_insumo` (`id_insumo`),
  KEY `fk_ri_medida` (`id_medida`),
  CONSTRAINT `fk_ri_insumo` FOREIGN KEY (`id_insumo`) REFERENCES `insumos` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_ri_medida` FOREIGN KEY (`id_medida`) REFERENCES `medidas` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_ri_recipe` FOREIGN KEY (`id_receta`) REFERENCES `recetario` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insumos_recetas`
--

LOCK TABLES `insumos_recetas` WRITE;
/*!40000 ALTER TABLE `insumos_recetas` DISABLE KEYS */;
/*!40000 ALTER TABLE `insumos_recetas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medidas`
--

DROP TABLE IF EXISTS `medidas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medidas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `abreviatura` varchar(20) DEFAULT NULL,
  `descripcion` text,
  `cantidad` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medidas`
--

LOCK TABLES `medidas` WRITE;
/*!40000 ALTER TABLE `medidas` DISABLE KEYS */;
/*!40000 ALTER TABLE `medidas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimientos_invetario`
--

DROP TABLE IF EXISTS `movimientos_invetario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimientos_invetario` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `movimiento_tipo` enum('entrada','salida','ajuste','produccion','venta','devolucion','traslado') NOT NULL,
  `referencia_tipo` varchar(100) DEFAULT NULL,
  `referencia_id` bigint DEFAULT NULL,
  `tipo_elemento` enum('insumo','producto') NOT NULL,
  `cantidad` decimal(18,4) NOT NULL,
  `costo_unitario` decimal(18,4) DEFAULT '0.0000',
  `id_usuario` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `notas` text,
  PRIMARY KEY (`id`),
  KEY `fk_inv_item_usuario` (`id_usuario`),
  CONSTRAINT `fk_inv_item_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientos_invetario`
--

LOCK TABLES `movimientos_invetario` WRITE;
/*!40000 ALTER TABLE `movimientos_invetario` DISABLE KEYS */;
/*!40000 ALTER TABLE `movimientos_invetario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ordenes_compra`
--

DROP TABLE IF EXISTS `ordenes_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ordenes_compra` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `id_proveedor` int NOT NULL,
  `id_usuario` int DEFAULT NULL,
  `fecha_pedido` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_entrega_estimada` date DEFAULT NULL,
  `estado` enum('borrador','enviado','recibido','cancelado') DEFAULT 'borrador',
  `notas` text,
  `total` decimal(18,4) DEFAULT '0.0000',
  PRIMARY KEY (`id`),
  KEY `fk_po_proveedor` (`id_proveedor`),
  KEY `fk_po_usuario` (`id_usuario`),
  CONSTRAINT `fk_po_proveedor` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_po_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ordenes_compra`
--

LOCK TABLES `ordenes_compra` WRITE;
/*!40000 ALTER TABLE `ordenes_compra` DISABLE KEYS */;
/*!40000 ALTER TABLE `ordenes_compra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `produccion`
--

DROP TABLE IF EXISTS `produccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `produccion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `id_producto` int NOT NULL,
  `lote_codigo` varchar(150) DEFAULT NULL,
  `cantidad_producida` decimal(18,4) NOT NULL,
  `fecha_produccion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `id_usuario` int DEFAULT NULL,
  `estado` enum('pendiente','completado','cancelado') DEFAULT 'completado',
  `notas` text,
  PRIMARY KEY (`id`),
  KEY `fk_prod_producto` (`id_producto`),
  KEY `fk_prod_usuario` (`id_usuario`),
  CONSTRAINT `fk_prod_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_prod_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `produccion`
--

LOCK TABLES `produccion` WRITE;
/*!40000 ALTER TABLE `produccion` DISABLE KEYS */;
/*!40000 ALTER TABLE `produccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `production_consumptions`
--

DROP TABLE IF EXISTS `production_consumptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `production_consumptions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `production_batch_id` bigint NOT NULL,
  `insumo_id` int NOT NULL,
  `cantidad_consumida` decimal(18,6) NOT NULL,
  `costo_unitario` decimal(18,6) DEFAULT '0.000000',
  `lote_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_pc_batch` (`production_batch_id`),
  KEY `fk_pc_insumo` (`insumo_id`),
  KEY `fk_pc_lote` (`lote_id`),
  CONSTRAINT `fk_pc_batch` FOREIGN KEY (`production_batch_id`) REFERENCES `produccion` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_pc_insumo` FOREIGN KEY (`insumo_id`) REFERENCES `insumos` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_pc_lote` FOREIGN KEY (`lote_id`) REFERENCES `stock` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `production_consumptions`
--

LOCK TABLES `production_consumptions` WRITE;
/*!40000 ALTER TABLE `production_consumptions` DISABLE KEYS */;
/*!40000 ALTER TABLE `production_consumptions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `id_medida` int NOT NULL,
  `cantidad_disponible` decimal(18,4) DEFAULT '0.0000',
  `stock_minimo` decimal(18,4) DEFAULT '0.0000',
  `stock_maximo` decimal(18,4) DEFAULT NULL,
  `bloqueado` tinyint(1) DEFAULT '0',
  `estado` enum('activo','inactivo') DEFAULT 'activo',
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_producto_medida` (`id_medida`),
  CONSTRAINT `fk_producto_medida` FOREIGN KEY (`id_medida`) REFERENCES `medidas` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedor_contactos`
--

DROP TABLE IF EXISTS `proveedor_contactos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedor_contactos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_proveedor` int NOT NULL,
  `nombre` varchar(150) DEFAULT NULL,
  `cargo` varchar(100) DEFAULT NULL,
  `correo` varchar(255) DEFAULT NULL,
  `telefono` varchar(50) DEFAULT NULL,
  `notas` text,
  PRIMARY KEY (`id`),
  KEY `fk_prov_contacto` (`id_proveedor`),
  CONSTRAINT `fk_prov_contacto` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedor_contactos`
--

LOCK TABLES `proveedor_contactos` WRITE;
/*!40000 ALTER TABLE `proveedor_contactos` DISABLE KEYS */;
/*!40000 ALTER TABLE `proveedor_contactos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedores`
--

DROP TABLE IF EXISTS `proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre_contacto` varchar(150) NOT NULL,
  `empresa` varchar(200) DEFAULT NULL,
  `correo` varchar(255) DEFAULT NULL,
  `nit` varchar(100) DEFAULT NULL,
  `telefono` varchar(50) DEFAULT NULL,
  `direccion` text,
  `estado` enum('activo','inactivo') DEFAULT 'activo',
  `observaciones` text,
  `deleted_at` timestamp NULL DEFAULT NULL,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores`
--

LOCK TABLES `proveedores` WRITE;
/*!40000 ALTER TABLE `proveedores` DISABLE KEYS */;
/*!40000 ALTER TABLE `proveedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recetario`
--

DROP TABLE IF EXISTS `recetario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recetario` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `id_producto` int NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `id_usuario` int DEFAULT NULL,
  `cantidad_insumo` int DEFAULT NULL,
  `tipo_medida` varchar(50) DEFAULT NULL,
  `nombre_medida` varchar(50) DEFAULT NULL,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_recipe_producto` (`id_producto`),
  KEY `fk_recetario_usuarios` (`id_usuario`),
  CONSTRAINT `fk_recetario_usuarios` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `fk_recipe_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recetario`
--

LOCK TABLES `recetario` WRITE;
/*!40000 ALTER TABLE `recetario` DISABLE KEYS */;
/*!40000 ALTER TABLE `recetario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recuperarpassword`
--

DROP TABLE IF EXISTS `recuperarpassword`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recuperarpassword` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `token` varchar(255) NOT NULL,
  `expires_at` datetime NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `used` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `fk_rp_usuario` (`id_usuario`),
  CONSTRAINT `fk_rp_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recuperarpassword`
--

LOCK TABLES `recuperarpassword` WRITE;
/*!40000 ALTER TABLE `recuperarpassword` DISABLE KEYS */;
/*!40000 ALTER TABLE `recuperarpassword` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sesiones_usuario`
--

DROP TABLE IF EXISTS `sesiones_usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sesiones_usuario` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `session_token` varchar(255) NOT NULL,
  `ip` varchar(50) DEFAULT NULL,
  `user_agent` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_activity` timestamp NULL DEFAULT NULL,
  `revoked_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_token` (`session_token`),
  KEY `fk_ses_usuario` (`id_usuario`),
  CONSTRAINT `fk_ses_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sesiones_usuario`
--

LOCK TABLES `sesiones_usuario` WRITE;
/*!40000 ALTER TABLE `sesiones_usuario` DISABLE KEYS */;
/*!40000 ALTER TABLE `sesiones_usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock`
--

DROP TABLE IF EXISTS `stock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stock` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `item_type` enum('insumo','producto') NOT NULL,
  `item_id` int NOT NULL,
  `id_ubicacion` int DEFAULT NULL,
  `cantidad` decimal(18,4) NOT NULL DEFAULT '0.0000',
  `fecha_lote` date DEFAULT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  `id_proveedor` int DEFAULT NULL,
  `costo_unitario` decimal(18,4) DEFAULT '0.0000',
  `lote_codigo` varchar(150) DEFAULT NULL,
  `creado_en` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_lote_ubicacion` (`id_ubicacion`),
  KEY `fk_lote_proveedor` (`id_proveedor`),
  KEY `item_type` (`item_type`,`item_id`),
  CONSTRAINT `fk_lote_proveedor` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_lote_ubicacion` FOREIGN KEY (`id_ubicacion`) REFERENCES `ubicaciones` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock`
--

LOCK TABLES `stock` WRITE;
/*!40000 ALTER TABLE `stock` DISABLE KEYS */;
/*!40000 ALTER TABLE `stock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ubicaciones`
--

DROP TABLE IF EXISTS `ubicaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ubicaciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `descripcion` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ubicaciones`
--

LOCK TABLES `ubicaciones` WRITE;
/*!40000 ALTER TABLE `ubicaciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `ubicaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `estado` enum('activo','inactivo') DEFAULT 'activo',
  `telefono` varchar(50) DEFAULT NULL,
  `id_rol` int DEFAULT NULL,
  `fecha_registro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `id_rol` (`id_rol`),
  CONSTRAINT `fk_usuarios_rol` FOREIGN KEY (`id_rol`) REFERENCES `roles` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `venta_productos`
--

DROP TABLE IF EXISTS `venta_productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `venta_productos` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `id_venta` bigint NOT NULL,
  `id_producto` int NOT NULL,
  `cantidad` decimal(18,4) NOT NULL,
  `precio_unitario` decimal(18,4) NOT NULL,
  `subtotal` decimal(18,4) GENERATED ALWAYS AS ((`cantidad` * `precio_unitario`)) VIRTUAL,
  PRIMARY KEY (`id`),
  KEY `fk_vi_venta` (`id_venta`),
  KEY `fk_vi_producto` (`id_producto`),
  CONSTRAINT `fk_vi_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_vi_venta` FOREIGN KEY (`id_venta`) REFERENCES `ventas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venta_productos`
--

LOCK TABLES `venta_productos` WRITE;
/*!40000 ALTER TABLE `venta_productos` DISABLE KEYS */;
/*!40000 ALTER TABLE `venta_productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `id_usuario` int DEFAULT NULL,
  `fecha_venta` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `total` decimal(18,4) DEFAULT '0.0000',
  `metodo_pago` varchar(100) DEFAULT NULL,
  `estado` enum('completada','anulada') DEFAULT 'completada',
  `cierre_caja_id` bigint DEFAULT NULL,
  `notas` text,
  PRIMARY KEY (`id`),
  KEY `fk_venta_usuario` (`id_usuario`),
  CONSTRAINT `fk_venta_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-09 20:51:31

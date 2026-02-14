# RF016: Registro de ventas y control de producto terminado

---

## Identificación

| Campo             | Valor                                           |
| ----------------- | ----------------------------------------------- |
| **ID**            | RF-019                                          |
| **Nombre**        | Registro de Ventas y Control de Producto Terminado |
| **Módulo**        | Ventas / Inventario / Punto de Venta            |
| **Prioridad**     | Alta                                            |
| **Estado**        | Pendiente de implementación                     |
| **Fecha**         | Febrero 2026                                    |

---

# Descripción

El sistema debe permitir registrar, consultar y controlar el stock disponible de productos terminados (panes, pasteles y otros productos listos para la venta) en cada punto de venta o sitio.

El inventario de producto terminado debe actualizarse automáticamente mediante:

- Entradas por producción confirmada (RF013).  
- Salidas por ventas registradas.  
- Ajustes manuales de inventario debidamente autorizados.  

El sistema debe:

- Reflejar las cantidades disponibles en tiempo real.  
- Impedir ventas que generen inventario negativo.  
- Generar alertas automáticas cuando el stock esté por debajo del mínimo configurado para cada producto.  

Esta funcionalidad garantiza control operativo en el punto de venta y precisión en la disponibilidad real de productos.

---

## Entradas

| Campo                    | Tipo              | Obligatorio | Validaciones                                                                 |
| ------------------------ | ----------------- | ----------- | ---------------------------------------------------------------------------- |
| `product_id`             | UUID / Entero     | Sí          | Debe existir como producto terminado registrado                              |
| `site_id`                | UUID / Entero     | Sí          | Debe existir como punto de venta válido                                      |
| `movement_type`          | Enum              | Sí          | Valores permitidos: `PRODUCTION`, `SALE`, `ADJUSTMENT`                      |
| `quantity`               | Decimal           | Sí          | Mayor a 0                                                                    |
| `reason`                 | Texto             | Condicional | Obligatorio si `movement_type = ADJUSTMENT`                                  |
| `user_id`                | UUID / Entero     | Sí          | Usuario autenticado con permisos válidos                                     |
| `timestamp`              | Fecha/Hora        | Sí          | Generado automáticamente por el sistema                                      |

---

# 5. Proceso paso a paso del requerimiento

## Registro de Producción Confirmada

1. Se confirma una orden de producción (RF013).  
2. El sistema identifica el producto terminado y la cantidad producida.  
3. Se genera automáticamente un movimiento tipo `PRODUCTION`.  
4. El stock del producto terminado se incrementa en tiempo real.  

## Registro de Venta

1. El usuario registra una venta en el punto de venta.  
2. El sistema valida que el stock disponible sea suficiente.  
3. Si la cantidad solicitada supera el stock, se bloquea la operación.  
4. Si la validación es correcta, se genera un movimiento tipo `SALE`.  
5. El sistema descuenta automáticamente la cantidad vendida del inventario.  

## Ajuste Manual de Inventario

1. Un usuario con rol autorizado accede al módulo de ajustes.  
2. Ingresa el producto, cantidad y motivo del ajuste.  
3. El sistema valida permisos del usuario.  
4. Se registra un movimiento tipo `ADJUSTMENT`.  
5. El sistema actualiza el stock y genera un registro de auditoría.  

---

## Salidas

| Escenario                                  | Código HTTP | Respuesta                                                                 |
| ------------------------------------------ | ----------- | ------------------------------------------------------------------------- |
| Movimiento registrado exitosamente         | 201         | Datos del movimiento y stock actualizado                                  |
| Stock insuficiente para la venta           | 400         | Mensaje de error: "Insufficient stock available"                          |
| Usuario sin permisos para ajuste           | 403         | Mensaje de error: "Unauthorized inventory adjustment"                     |
| Producto o sitio no encontrado             | 404         | Mensaje de error: "Resource not found"                                    |
| Error de validación                        | 422         | Detalle de errores de validación                                           |

---

## Endpoint Asociado

| Método | Ruta                                           | Auth requerida |
| ------ | ---------------------------------------------- | -------------- |
| POST   | `/api/v1/finished-products/movements`          | Sí             |
| GET    | `/api/v1/finished-products/stock`              | Sí             |
| GET    | `/api/v1/finished-products/movements`          | Sí             |

---

# Reglas de Negocio

1. **Autorización de Ajustes**  
   Solo usuarios con rol administrativo o autorizado pueden realizar ajustes manuales.  
   Usuarios con rol de consulta solo pueden visualizar el inventario.

2. **Sincronización en Tiempo Real**  
   El stock debe actualizarse inmediatamente tras la confirmación de cualquier movimiento (producción, venta o ajuste).

3. **Restricción de Inventario Negativo**  
   No se permite registrar ventas que superen el stock disponible.

4. **Trazabilidad de Movimientos**  
   Todo movimiento debe registrar:
   - ID del usuario  
   - Tipo de movimiento  
   - Fecha y hora  
   - Motivo (si aplica)  

5. **Alertas de Stock Mínimo**  
   El sistema debe generar alertas automáticas cuando el inventario disponible sea menor al stock mínimo configurado para el producto.

6. **Integridad del Producto**  
   Solo pueden registrarse movimientos sobre productos terminados previamente creados y activos en el sistema.

---

# Impacto en el Sistema

Este requerimiento permite:

- Control preciso del inventario en punto de venta.  
- Prevención de sobreventa.  
- Trazabilidad completa de movimientos.  
- Información confiable para reportes financieros y operativos.  
- Sincronización directa con producción e inventario general del sistema.

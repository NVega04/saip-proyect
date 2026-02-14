# RF020: Registro de ventas de productos terminados

---

## Identificación

| Campo             | Valor                                      |
| ----------------- | ------------------------------------------ |
| **ID**            | RF-020                                     |
| **Nombre**        | Registro de Ventas de Productos Terminados |
| **Módulo**        | Ventas / Punto de Venta / Inventario       |
| **Prioridad**     | Alta                                       |
| **Estado**        | Pendiente de implementación                |
| **Fecha**         | Febrero 2026                               |

---

# 3. Descripción

El sistema debe permitir registrar las ventas de productos terminados de forma detallada, indicando:

- Productos vendidos  
- Cantidades  
- Precio aplicado  
- Impuestos  
- Descuentos  

Cada registro de venta debe generar automáticamente una salida en el inventario de productos terminados (RF016), asegurando que el stock disponible se actualice en tiempo real y refleje la realidad comercial del establecimiento.

El sistema debe garantizar:

- Control de inventario en tiempo real.  
- Prevención de ventas con stock insuficiente.  
- Cálculo automático del total con impuestos y descuentos.  
- Trazabilidad completa ante anulaciones o modificaciones posteriores.

---

## Entradas

| Campo                | Tipo              | Obligatorio | Validaciones                                                                 |
| -------------------- | ----------------- | ----------- | ---------------------------------------------------------------------------- |
| `sale_id`            | UUID / Entero     | Sí          | Generado automáticamente                                                     |
| `product_id`         | UUID / Entero     | Sí          | Debe existir como producto terminado activo                                  |
| `quantity`           | Decimal           | Sí          | Mayor a 0 y no superior al stock disponible                                  |
| `unit_price`         | Decimal           | Sí          | Mayor o igual a 0                                                             |
| `discount`           | Decimal (%)       | No          | Entre 0 y 100                                                                 |
| `tax`                | Decimal (%)       | Sí          | Según configuración tributaria del producto                                  |
| `total_amount`       | Decimal           | Sí          | Calculado automáticamente por el sistema                                      |
| `user_id`            | UUID / Entero     | Sí          | Usuario autenticado con rol autorizado                                        |
| `justification`      | Texto             | Condicional | Obligatorio en caso de anulación o modificación posterior                     |
| `timestamp`          | Fecha/Hora        | Sí          | Generado automáticamente por el sistema                                        |

---

# 5. Proceso Paso a Paso del Requerimiento

## Registro de Venta

1. El usuario accede al módulo de Ventas.  
2. El sistema valida que el usuario tenga rol **Administrador** o **Vendedor**.  
3. El sistema muestra el stock actual disponible por producto.  
4. El usuario selecciona el producto y la cantidad.  
5. El sistema valida:
   - Que el producto exista y esté activo.  
   - Que la cantidad no supere el stock disponible.  
6. El sistema calcula automáticamente:
   - Subtotal  
   - Descuentos aplicables  
   - Impuestos  
   - Total final  
7. El usuario confirma la venta.  
8. El sistema:
   - Registra la venta en la base de datos.  
   - Genera automáticamente un movimiento de salida en inventario (RF016).  
   - Actualiza el stock en tiempo real.  
   - Evalúa si el producto queda por debajo del stock mínimo y genera alerta visual si aplica.  
   - Registra la operación en auditoría.  

## Anulación o Modificación

1. El usuario autorizado solicita anulación o modificación.  
2. Debe ingresar una justificación obligatoria.  
3. El sistema registra el cambio en auditoría.  
4. El inventario se ajusta automáticamente según corresponda.

---

## Salidas

| Escenario                                  | Código HTTP | Respuesta                                                                  |
| ------------------------------------------ | ----------- | -------------------------------------------------------------------------- |
| Venta registrada exitosamente              | 201         | Datos de la venta y stock actualizado                                      |
| Stock insuficiente                         | 400         | Mensaje de error: "Insufficient stock available"                           |
| Usuario sin permisos                       | 403         | Mensaje de error: "Unauthorized action"                                    |
| Producto no encontrado                     | 404         | Mensaje de error: "Product not found"                                      |
| Error de validación                        | 422         | Detalle de errores de validación                                            |

---

## Endpoint Asociado

| Método | Ruta                          | Auth requerida |
| ------ | ----------------------------- | -------------- |
| POST   | `/api/v1/sales`               | Sí             |
| GET    | `/api/v1/sales/{id}`          | Sí             |
| PUT    | `/api/v1/sales/{id}`          | Sí             |
| GET    | `/api/v1/products/stock`      | Sí             |

---

# 7. Reglas de Negocio

1. **Control de Acceso**  
   Solo usuarios con rol **Administrador** o **Vendedor** pueden registrar ventas.

2. **Restricción de Inventario Negativo**  
   No se permite registrar ventas con cantidades superiores al stock disponible.

3. **Cálculo Automático**  
   El sistema debe calcular automáticamente el total de la venta incluyendo:
   - Impuestos configurados  
   - Descuentos aplicables  

4. **Actualización Inmediata de Inventario**  
   Cada venta registrada genera automáticamente una salida en el inventario de productos terminados (RF016).

5. **Alertas de Stock Mínimo**  
   Si el stock resultante es inferior al mínimo configurado, el sistema debe emitir una alerta visual automática.

6. **Trazabilidad Obligatoria**  
   - Toda venta debe quedar registrada con usuario, fecha y hora.  
   - Cualquier anulación o modificación requiere justificación obligatoria.  
   - Todos los cambios deben quedar registrados en el historial de auditoría.

7. **Integridad Operativa**  
   El inventario debe reflejar correctamente:
   - Entradas por producción confirmada (RF013).  
   - Salidas por ventas registradas.  
   - Ajustes manuales autorizados.

---

# Impacto en el Sistema

Este requerimiento garantiza:

- Control comercial preciso.  
- Sincronización total entre ventas e inventario.  
- Prevención de sobreventa.  
- Información confiable para reportes financieros y operativos.  
- Trazabilidad completa para auditoría interna.

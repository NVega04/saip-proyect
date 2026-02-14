# RF015: Asociación de Inventario de Insumos con Recetas


## Identificación

| Campo             | Valor                                                   |
| ----------------- | ------------------------------------------------------- |
| **ID**            | RF-015                                                  |
| **Nombre**        | Asociación de Inventario de Insumos con Recetas         |
| **Módulo**        | Producción / Recetas / Inventario                       |
| **Prioridad**     | Alta                                                    |
| **Estado**        | Pendiente de implementación                             |
| **Fecha**         | Febrero 2026                                            |

---

# 3. Descripción

El sistema debe permitir la configuración técnica de las recetas vinculando los insumos (materias primas) previamente registrados en el **RF007**.  

Esta funcionalidad permite definir la composición exacta de cada producto de panadería, especificando:

- Cantidades requeridas  
- Unidades de medida  
- Porcentajes de merma  
- Nivel de stock mínimo asociado  

Este requerimiento es un componente esencial para:

- Calcular el costo real de producción.  
- Ejecutar el descuento automático de inventario al registrar una producción.  
- Garantizar trazabilidad y consistencia en el control de inventarios.  

Sin una asociación robusta entre recetas e insumos, el control de inventarios sería impreciso y afectaría procesos posteriores como el descuento automático de materias primas.

---

## Entradas

| Campo                    | Tipo              | Obligatorio | Validaciones                                                                 |
| ------------------------ | ----------------- | ----------- | ---------------------------------------------------------------------------- |
| `recipe_id`              | UUID / Entero     | Sí          | Debe existir en el módulo de recetas                                         |
| `ingredient_id`          | UUID / Entero     | Sí          | Debe existir previamente en el módulo de inventario (RF007)                 |
| `quantity`               | Decimal           | Sí          | Mayor a 0                                                                    |
| `unit_of_measure`        | Texto             | Sí          | Debe coincidir con la unidad configurada en el maestro de insumos           |
| `waste_percentage`       | Decimal (%)       | No          | Entre 0 y 100                                                                |
| `substitute_ingredient`  | UUID / Entero     | No          | Si se define, debe tener unidad compatible o factor de conversión definido  |
| `minimum_stock_level`    | Decimal           | No          | Mayor o igual a 0                                                            |

---

# 5. Proceso Paso a Paso del Requerimiento

1. El usuario accede a la ficha técnica de una receta existente.  
2. El sistema muestra un listado filtrable de los insumos disponibles en inventario.  
3. El usuario selecciona un insumo.  
4. El usuario ingresa:
   - Cantidad requerida  
   - Unidad de medida  
   - Nivel de stock mínimo (opcional)  
5. El sistema valida:
   - Que el insumo exista en inventario (RF007).  
   - Que no esté duplicado dentro de la misma receta.  
   - Que la unidad de medida sea válida y coincidente.  
6. El usuario guarda la configuración.  
7. El sistema:
   - Persiste la asociación en base de datos.  
   - Actualiza inmediatamente la ficha técnica del producto.  
   - Genera automáticamente un registro de auditoría (log).  

---

## Salidas

| Escenario                                  | Código HTTP | Respuesta                                                                 |
| ------------------------------------------ | ----------- | ------------------------------------------------------------------------- |
| Asociación creada exitosamente             | 201         | Datos de la asociación creada                                             |
| Insumo duplicado en la receta              | 400         | Mensaje de error: "Ingredient already associated to recipe"               |
| Insumo inexistente                         | 404         | Mensaje de error: "Ingredient not found in inventory"                     |
| Unidad incompatible                        | 422         | Detalle de error de validación de unidad                                  |
| Error de validación general                | 422         | Detalle de los errores de validación                                      |

---

## Endpoint Asociado

| Método | Ruta                                      | Auth requerida |
| ------ | ------------------------------------------ | -------------- |
| POST   | `/api/v1/recipes/{recipe_id}/ingredients` | Sí             |
| PUT    | `/api/v1/recipes/{recipe_id}/ingredients/{id}` | Sí        |
| DELETE | `/api/v1/recipes/{recipe_id}/ingredients/{id}` | Sí        |

---

# 7. Reglas de Negocio

1. **Validación de Unicidad**  
   No se permite asociar el mismo insumo más de una vez dentro de una misma receta.

2. **Gestión de Sustitutos**  
   Si se define un insumo sustituto:
   - Debe tener unidad de medida compatible, o  
   - Debe existir un factor de conversión previamente configurado.

3. **Integridad de Datos**  
   Solo pueden asociarse insumos creados previamente en el módulo de inventario (RF007).

4. **Stock Mínimo Parametrizable**  
   Cada insumo asociado puede tener un nivel mínimo de stock configurado para alertar sobre la viabilidad de producción.

5. **Trazabilidad (Log de Auditoría)**  
   Cualquier creación, modificación o eliminación de asociación debe generar un registro histórico que incluya:
   - Usuario responsable  
   - Fecha  
   - Hora  
   - Detalle del cambio realizado  

6. **Validación de Unidades**  
   Las unidades ingresadas deben coincidir con las configuradas en el maestro de insumos para evitar errores de conversión y cálculos incorrectos.

---

# Impacto en el Sistema

Este requerimiento garantiza que los datos utilizados posteriormente en el proceso de descuento automático de materias primas sean precisos y confiables.

Permite:

- Cálculo correcto de costos de producción.  
- Descuento automático exacto de inventario.  
- Planeación de producción basada en disponibilidad real.  
- Trazabilidad completa ante auditorías internas.  

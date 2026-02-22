# RNF-002 — Rendimiento

---

## Identificación

| Campo | Valor |
| --- | --- |
| **ID** | RNF-002 |
| **Nombre** | Rendimiento |
| **Categoría** | Desempeño y escalabilidad |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

---

## Requisitos

### RNF-002.1 — Tiempo de respuesta en consultas de lectura

Las operaciones de consulta más frecuentes deben responder rápidamente incluso con volúmenes moderados de datos:

- Consulta de stock de insumos (inventario general o por categoría): **≤ 600 ms** (percentil 95)
- Consulta de stock de productos terminados: **≤ 700 ms** (percentil 95)
- Visualización de receta individual (ingredientes + cantidades): **≤ 500 ms** (percentil 95)
- Listado de producción diaria reciente: **≤ 800 ms** (percentil 95)

Medido bajo carga normal (20–30 usuarios concurrentes) y con ~10.000 registros en tablas principales.

### RNF-002.2 — Tiempo de respuesta en operaciones de escritura críticas

Las acciones que modifican inventario deben ser rápidas y atómicas:

- Entrada de insumos al inventario (actualización de cantidades): **≤ 1.2 segundos** (percentil 99)
- Descontado automático de materias primas al registrar producción: **≤ 1.5 segundos** (percentil 99)
- Registro de venta de producto terminado (actualización de stock): **≤ 1.2 segundos** (percentil 99)

Todas estas operaciones deben garantizar **consistencia** (transacciones ACID) y no permitir sobre-descontado (stock negativo no autorizado).

### RNF-002.3 — Capacidad de usuarios concurrentes

El sistema debe soportar un número mínimo de usuarios simultáneos sin degradación significativa:

- Mínimo soportado: **50 usuarios concurrentes** realizando operaciones mixtas (consultas + escrituras)
- Bajo esta carga: tiempos de respuesta no deben aumentar más del **50%** respecto a prueba con 1 usuario
- Recomendado objetivo: **100 usuarios concurrentes** con degradación aceptable (< 2× tiempo base)

### RNF-002.4 — Optimización de consultas pesadas

Consultas que involucran joins múltiples o agregaciones deben estar optimizadas:

- Reportes de consumo mensual de insumos por receta/producto: **≤ 3 segundos** (percentil 95)
- Cálculo de stock proyectado (considerando recetas y producción pendiente): **≤ 2.5 segundos** (percentil 95)

Se deben implementar índices adecuados en columnas frecuentes (id_insumo, id_producto, fecha_produccion, etc.) y considerar vistas materializadas si el volumen lo justifica.

### RNF-002.5 — Manejo de carga pico (ventas/producción)

Durante picos de actividad (ej. cierre de turno, registro masivo de producción):

- El sistema no debe presentar errores 5xx ni timeouts > 10 segundos
- Implementar **rate limiting suave** en endpoints de escritura masiva si es necesario
- Priorizar operaciones críticas (descontado de insumos y registro de ventas) sobre consultas reportes

### RNF-002.6 — Monitoreo de rendimiento

Implementar logging de tiempos de ejecución en endpoints clave:

- Registrar en logs (o en herramienta como Sentry/New Relic si se integra): tiempo de respuesta, endpoint, método, usuario (anonimizado), tamaño de respuesta
- Alertar si percentil 99 > 5 segundos en operaciones críticas durante más de 5 minutos

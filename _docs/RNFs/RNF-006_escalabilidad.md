# RNF-006 — Escalabilidad

---

## Identificación

| Campo | Valor |
| --- | --- |
| **ID** | RNF-006 |
| **Nombre** | Escalabilidad |
| **Categoría** | Capacidad de crecimiento horizontal y vertical |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

---

## Requisitos

### RNF-006.1 — Escalabilidad de volumen de datos

El sistema debe soportar un crecimiento significativo en el número de registros sin degradación notable:

- Insumos y productos terminados: hasta **50.000** registros cada uno
- Recetas: hasta **5.000** recetas activas (con un promedio de 10–20 insumos por receta)
- Registros de producción: hasta **100.000** entradas anuales
- Registros de ventas: hasta **200.000** transacciones anuales
- Proveedores y contactos: hasta **2.000** registros

En estos volúmenes, los tiempos de respuesta de consultas críticas no deben superar los definidos en RNF-002 (percentiles 95/99).

### RNF-006.2 — Escalabilidad horizontal de usuarios concurrentes

Soporte para aumento de usuarios simultáneos mediante réplicas:

- Objetivo inicial: 50–100 usuarios concurrentes (cumplir RNF-002.3)
- Capacidad objetivo a mediano plazo (1–2 años): **≥ 300 usuarios concurrentes** con degradación ≤ 2× en tiempos de respuesta
- Diseño que permita agregar instancias de la API/backend sin cambios en código (stateless services)
- Uso de balanceador de carga (load balancer) con sticky sessions solo si es estrictamente necesario (preferir JWT stateless)

### RNF-006.3 — Escalabilidad de base de datos

La base de datos debe permitir crecimiento vertical y, en futuro, horizontal:

- Soporte para réplicas de lectura (read replicas) para distribuir consultas pesadas (reportes, consultas de stock, recetas)
- Posibilidad futura de sharding por entidad clave (ej. por sucursal si se implementa multi-sucursal)
- Índices adecuados en columnas de búsqueda frecuente (nombre insumo/producto, fechas de producción/venta, códigos)
- Evitar consultas N+1 en joins frecuentes (recetas → insumos, producción → recetas)
- Monitoreo de tamaño de tablas y queries lentas (> 1 segundo) para optimización proactiva

### RNF-006.4 — Escalabilidad de escritura (transacciones críticas)

Operaciones de alta frecuencia deben soportar incremento de carga:

- Entradas/salidas de inventario y registro de producción: capacidad para **≥ 20 transacciones por segundo** (pico)
- Registro de ventas: capacidad para **≥ 30 transacciones por segundo** (pico, ej. fin de turno)
- Implementar colas asíncronas (Celery, Redis Queue o similar) para operaciones no críticas (notificaciones, reportes generados)
- Uso de transacciones optimistas o pesimistas según el caso para evitar bloqueos prolongados

### RNF-006.5 — Diseño preparado para multi-sucursal (futuro)

Aunque no sea requisito inicial, el modelo de datos y arquitectura deben facilitar futura expansión:

- Campo sucursal_id o tenant_id en tablas principales (insumos, productos, producción, ventas)
- Filtros por sucursal por defecto en consultas de usuarios no globales
- Posibilidad de aislamiento lógico de datos por sucursal (row-level security o esquemas separados)
- Reportes consolidados y por sucursal sin modificaciones estructurales mayores

### RNF-006.6 — Escalabilidad de almacenamiento de archivos (opcional)

Si se implementan imágenes/fotos (recetas, productos, insumos):

- Almacenamiento externo (S3, Cloudinary, MinIO) en lugar de base de datos o filesystem local
- URLs firmadas y con expiración para acceso seguro
- Caché de imágenes en CDN para reducir latencia en consultas repetitivas

### RNF-006.7 — Monitoreo y alertas de escalabilidad

Detectar cuellos de botella antes de que afecten a los usuarios:

- Métricas clave: número de usuarios concurrentes, transacciones/segundo, uso de CPU/memoria por instancia, longitud de colas, latencia de base de datos
- Alertas ante: uso > 80% sostenido de CPU/memoria, aumento > 50% en tiempo de respuesta promedio, colas con backlog > 100 tareas
- Dashboard (Grafana, similar) con tendencias mensuales de crecimiento (usuarios, transacciones, tamaño BD)

### RNF-006.8 — Plan de crecimiento progresivo

Estrategia definida para escalar sin downtime mayor:

- Fase 1 (actual): servidor único + base de datos única (vertical)
- Fase 2: múltiples instancias API + balanceador + réplicas lectura BD
- Fase 3: introducción de colas asíncronas + sharding o particionamiento si se alcanza > 500 usuarios o > 1M transacciones/año
- Documento con umbrales de activación de cada fase (basados en métricas reales)

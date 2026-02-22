# RNF-009 — Auditoría y Trazabilidad

---

## Identificación

| Campo | Valor |
| --- | --- |
| **ID** | RNF-009 |
| **Nombre** | Auditoría y Trazabilidad |
| **Categoría** | Registro inmutable de acciones críticas y eventos del sistema |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

---

## Requisitos

### RNF-009.1 — Registro obligatorio de acciones críticas

Todas las operaciones que modifiquen datos sensibles o afecten el estado del negocio deben registrarse automáticamente:

- Autenticación: inicio de sesión, cierre de sesión, cambio/recuperación de contraseña
- Gestión de usuarios: creación, baja, cambio de rol, activación/desactivación
- Inventario de insumos: entradas, salidas manuales, ajustes por corrección, bajas por caducidad/pérdida
- Producción: registro de receta producida, cantidad, descontado automático de insumos
- Ventas: registro de venta, devolución, anulación
- Recetas: creación, edición, desactivación
- Proveedores: creación, edición, eliminación de contactos/proveedores
- Configuraciones del sistema: cambios en parámetros globales (si aplica)

### RNF-009.2 — Contenido mínimo de cada registro de auditoría

Cada entrada en la bitácora debe contener al menos:

- Timestamp (UTC + conversión a zona local America/Bogota al mostrar)
- ID del usuario que realizó la acción (o “sistema” para procesos automáticos)
- Nombre o email del usuario (anonimizado si aplica por privacidad)
- IP del cliente (opcional, configurable por privacidad)
- Tipo de acción (CREATE, UPDATE, DELETE, LOGIN, LOGOUT, ADJUST, etc.)
- Entidad afectada (ej. “insumo”, “receta”, “produccion”, “venta”)
- ID de la entidad afectada
- Descripción breve de la acción (ej. “Descontado 15 kg de harina por producción de 100 unidades”)
- Valores antiguos y nuevos (diff) para campos modificados (solo campos relevantes)
- Resultado: éxito / error (con código de error si aplica)

### RNF-009.3 — Inmutabilidad y protección de los registros

Los logs de auditoría deben ser inalterables una vez creados:

- Almacenamiento en tabla separada (audit_log) con campos de solo escritura (append-only)
- No permitir UPDATE ni DELETE en registros de auditoría (restringir en base de datos)
- Uso de triggers automáticos en PostgreSQL o similar para capturar cambios
- Hash o firma digital de cada registro (opcional avanzado: cadena de hashes para verificar integridad)
- Acceso de lectura restringido solo a roles de administrador o auditor

### RNF-009.4 — Retención y rotación de registros

Definir política de almacenamiento a largo plazo:

- Retención mínima: **2 años** para registros de auditoría (cumplir normativas contables y fiscales en Colombia)
- Retención recomendada: **5 años** para operaciones financieras (ventas, ajustes de inventario)
- Rotación automática: archivado a almacenamiento frío (S3 Glacier o similar) después de 1 año
- Borrado seguro solo después de expiración y con aprobación documentada

### RNF-009.5 — Búsqueda y consulta de auditoría

Interfaz administrativa para revisar historial:

- Filtros por: fecha (rango), usuario, tipo de acción, entidad, ID de entidad
- Ordenamiento por fecha descendente por defecto
- Paginación y exportación a CSV/PDF (con firma digital si aplica)
- Vista detallada de cada registro mostrando diff de cambios (antes/después)
- Búsqueda por texto libre en descripción o valores modificados

### RNF-009.6 — Alertas automáticas por eventos sensibles

Notificar en tiempo real o diferido ante acciones de alto riesgo:

- Múltiples intentos fallidos de login (brute force)
- Cambio de contraseña por usuario no administrador
- Baja o cambio de rol de usuario administrador
- Ajustes manuales de inventario que generen stock negativo o aumentos > umbral (ej. +50%)
- Anulaciones o devoluciones de ventas > umbral definido
- Envío por correo/SMS a administradores (configurable)

### RNF-009.7 — Integración con monitoreo externo (opcional avanzado)

Preparar los logs para herramientas externas:

- Formato estructurado (JSON) para fácil ingesta
- Soporte para envío a: ELK Stack (Elasticsearch + Kibana), Loki + Grafana, Datadog, Sentry (para errores)
- Campo correlation_id o request_id para rastrear una petición completa (frontend → backend → BD)

### RNF-009.8 — Cumplimiento normativo básico

Alinear la trazabilidad con requisitos comunes en Colombia:

- Registro de operaciones contables/fiscales (ventas, ajustes de inventario) para soporte de facturación electrónica
- Trazabilidad de movimientos de inventario para auditorías DIAN o contables
- Posibilidad de generar reportes de “quién hizo qué y cuándo” en menos de 5 minutos
- Documentación de la política de auditoría (incluida en manual del sistema)

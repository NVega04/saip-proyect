# RNF-003 — Disponibilidad

---

## Identificación

| Campo | Valor |
| --- | --- |
| **ID** | RNF-003 |
| **Nombre** | Disponibilidad |
| **Categoría** | Continuidad del servicio y recuperación |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

---

## Requisitos

### RNF-003.1 — Ventanas de mantenimiento programado

Las actualizaciones, parches de seguridad o migraciones de base de datos deben realizarse en horarios de bajo impacto:

- Máximo 4 horas por mes
- Preferentemente entre 00:00 y 05:00 hora local (Bogotá)
- Notificación previa mínima de 48 horas vía correo o dentro del sistema a administradores
- Durante mantenimiento: modo de solo lectura o mensaje informativo visible

### RNF-003.2 — Tiempo de recuperación ante fallos (RTO - Recovery Time Objective)

Tiempo máximo aceptable para restaurar el servicio completo tras una interrupción no planificada:

- RTO objetivo: **≤ 2 horas**
- RTO máximo aceptable: **≤ 4 horas**
- Incluye detección del fallo, diagnóstico, aplicación de solución (reinicio, rollback, restauración de backup, etc.)

### RNF-003.3 — Pérdida máxima de datos aceptable (RPO - Recovery Point Objective)

Cantidad máxima de datos que se permite perder en caso de fallo catastrófico:

- RPO objetivo: **≤ 15 minutos** (es decir, backups con frecuencia ≤ cada 15 min para datos críticos)
- RPO máximo aceptable: **≤ 60 minutos**
- Datos críticos incluyen: stock de insumos, stock de productos terminados, registros de producción del día, ventas recientes

### RNF-003.4 — Estrategia de respaldos automáticos

Implementar copias de seguridad automáticas y verificables:

- Respaldos completos diarios (a medianoche)
- Respaldos incrementales cada 4–6 horas (o cada 60 minutos para transacciones críticas si el volumen lo permite)
- Retención mínima: 30 días para respaldos diarios + 7 días para incrementales
- Almacenamiento en ubicación secundaria (diferente región o proveedor cloud si aplica)
- Pruebas de restauración trimestrales documentadas

### RNF-003.5 — Manejo de fallos parciales y alta disponibilidad básica

El sistema debe minimizar interrupciones totales:

- Separación de componentes críticos (base de datos, API, frontend) para permitir fallos aislados
- Implementar health-checks y auto-reinicio de servicios (ej. con Docker + orchestrator o systemd)
- En caso de fallo de un nodo/servicio: redirección automática o fallback a modo degradado (lectura sola)

### RNF-003.6 — Monitoreo y alertas de disponibilidad

Implementar supervisión continua:

- Monitoreo de uptime cada 1–5 minutos (ej. endpoint /health o similar)
- Alertas inmediatas (correo/SMS/Slack/Discord) ante downtime > 5 minutos
- Registro de incidentes con: hora de inicio, hora de detección, hora de resolución, causa raíz, impacto
- Dashboard visible para administradores con estado actual y SLA mensual

### RNF-003.7 — Plan de recuperación ante desastres (DR)

Definir procedimiento básico para escenarios graves (pérdida total de servidor principal, corte eléctrico prolongado, etc.):

- Documento con pasos claros (runbook)
- Prioridad: restaurar primero autenticación → inventario/stock → producción → ventas
- Prueba anual mínima del plan completo.

# RNF-005 — Mantenibilidad

---

## Identificación

| Campo | Valor |
| --- | --- |
| **ID** | RNF-005 |
| **Nombre** | Mantenibilidad |
| **Categoría** | Facilidad de mantenimiento, evolución y corrección de errores |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

---

## Requisitos

### RNF-005.1 — Arquitectura modular y limpia

El sistema debe seguir principios de arquitectura que faciliten cambios aislados:

- Separación clara de capas: presentación (frontend), aplicación (API/services), dominio (lógica de negocio), persistencia (repositorios/ORM)
- Módulos independientes por dominio: autenticación, inventario-insumos, recetas-producción, ventas, proveedores
- Dependencias unidireccionales (frontend → API → services → domain → persistence)

### RNF-005.2 — Código legible y estandarizado

Adoptar convenciones que permitan a cualquier desarrollador entender y modificar el código rápidamente:

- Comentarios solo donde aporten valor (no repetir lo obvio, explicar “por qué” no “qué”)
- Funciones/métodos cortos (máximo ~30–50 líneas recomendadas)

### RNF-005.3 — Cobertura de pruebas automatizadas

Implementar pruebas que den confianza al realizar cambios:

- Pruebas unitarias: ≥ 80% cobertura en lógica de negocio crítica (cálculos de recetas, descontado de stock, validaciones)
- Pruebas de integración: endpoints clave (autenticación, entradas/salidas inventario, registro producción/ventas)
- Pruebas end-to-end (E2E): flujos principales (login → registrar producción → verificar stock actualizado)

### RNF-005.4 — Documentación interna obligatoria

Mantener documentación actualizada y útil:

- README principal con: instalación, ejecución local, variables de entorno, arquitectura general (diagrama simple)

### RNF-005.5 — Logging estructurado y trazabilidad

Facilitar la depuración y el diagnóstico de problemas:

- Uso de logger estructurado (JSON logs recomendados) con niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Logs sensibles (contraseñas, tokens) nunca deben aparecer

### RNF-005.6 — Facilidad de despliegue y rollback

El proceso de despliegue debe ser rápido y reversible:

- Entornos diferenciados: dev, staging, production
- Rollback a versión anterior en < 10 minutos en caso de fallo crítico
- Variables de entorno por entorno (no hardcodear URLs, claves, etc.)

### RNF-005.7 — Monitoreo y alertas para mantenibilidad

Detectar problemas de código o degradación temprana:

- Métricas básicas: uso de CPU/memoria, errores 5xx, tiempo de respuesta promedio
- Alertas ante: aumento súbito de errores, caída en cobertura de tests, dependencias vulnerables detectadas
- Integración con herramienta de monitoreo (Sentry para errores, Prometheus/Grafana si aplica)

# RNF-007 — Compatibilidad y Portabilidad

---

## Identificación

| Campo | Valor |
| --- | --- |
| **ID** | RNF-007 |
| **Nombre** | Compatibilidad y Portabilidad |
| **Categoría** | Soporte multiplataforma, navegadores y entornos de ejecución |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

---

## Requisitos

### RNF-007.1 — Compatibilidad con navegadores web (frontend)

La interfaz debe funcionar correctamente en los navegadores más utilizados:

- Navegadores soportados (últimas dos versiones estables):
  - Google Chrome
  - Mozilla Firefox
  - Microsoft Edge
  - Safari (macOS e iOS)

### RNF-007.2 — Diseño responsive y compatibilidad con dispositivos

El frontend debe adaptarse a diferentes tamaños de pantalla y orientaciones:

- Resoluciones mínimas soportadas: 320px (móviles pequeños) hasta 4K (monitores grandes)
- Breakpoints principales: móvil (<768px), tablet (768–1023px), desktop (≥1024px)
- Uso de unidades relativas (%, vw/vh, rem/em) en lugar de píxeles fijos donde aplique
- Pruebas en dispositivos reales o emuladores: iPhone (Safari), Android (Chrome), tablets
- Evitar scroll horizontal innecesario; tablas deben tener scroll interno o tarjetas en móvil

### RNF-007.3 — Compatibilidad con sistemas operativos

El sistema debe ejecutarse sin modificaciones específicas en los SO más comunes:

- Servidor/Backend: Linux (Ubuntu/Debian preferido), Windows Server (si aplica en algunos entornos)
- Desarrollo local: Windows 10/11, macOS (Ventura/Sonoma+), Linux (cualquier distribución moderna)
- No dependencias exclusivas de un SO (ej. evitar paths con backslash sin normalización)

### RNF-007.4 — Portabilidad de la base de datos

La base de datos debe ser portable entre diferentes motores y proveedores:

- Motor principal: PostgreSQL (recomendado por robustez en transacciones ACID)
- Soporte secundario: SQLite (para desarrollo local y pruebas rápidas)
- Posibilidad futura de migración a otros motores (MySQL/MariaDB) con cambios mínimos (usar ORM como SQLAlchemy que abstraiga diferencias)
- Scripts de migración versionados (Alembic para PostgreSQL) y reversibles

### RNF-007.5 — Portabilidad del despliegue (entornos)

El sistema debe desplegarse fácilmente en diferentes plataformas:

- Dockerizado completo: Dockerfile para backend y frontend, docker-compose.yml para desarrollo (incluye BD, Redis si aplica, etc.)
- Soporte para orquestadores: Docker Compose (desarrollo), Kubernetes o Docker Swarm (producción futura)
- Variables de entorno estandarizadas para configuración (BD_URL, SECRET_KEY, etc.)

### RNF-007.6 — Compatibilidad con estándares web y APIs

Uso exclusivo de tecnologías estándar y bien soportadas:

- Frontend: HTML5, CSS3 (Flexbox/Grid), ES6+ JavaScript (o TypeScript)
- APIs: RESTful con JSON (OpenAPI/Swagger para documentación)
- Autenticación: JWT (HS256/RS256) o sesiones seguras, sin cookies de terceros innecesarias
- No uso de tecnologías obsoletas o con soporte limitado (Flash, WebSQL, etc.)

### RNF-007.7 — Soporte multiplataforma para impresión y exportación

Funcionalidades de salida (tickets de venta, reportes) deben ser consistentes:

- Impresión de tickets/recetas: formato A4 o ticket térmico (58/80mm) vía CSS @media print
- Exportación a PDF/Excel/CSV desde frontend o backend (usar librerías como pdfmake, openpyxl, pandas)
- Vista previa antes de imprimir/exportar
- Compatibilidad con impresoras estándar (sin drivers propietarios)

### RNF-007.8 — Pruebas de compatibilidad y regresión

Garantizar que los cambios no rompan la compatibilidad:

- Matriz de pruebas de compatibilidad (navegadores × dispositivos × SO) ejecutada antes de cada release mayor
- Smoke tests automatizados en CI/CD para al menos 3 combinaciones principales
- Registro de incidencias específicas de compatibilidad con capturas y pasos para reproducir

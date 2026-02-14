# SAIP - Sistema Administrativo Integral de Productos

## Objetivo del Proyecto

Desarrollar un **Sistema Administrativo Integral de Productos (SAIP)** en plataforma web, diseñado específicamente para pequeñas panaderías como La Parmesana, con el fin de:

- Automatizar y optimizar procesos clave: ventas, inventario, compras, proveedores, producción de materias primas y administración básica.
- Centralizar la información mediante formularios digitales y consultas en tiempo real.
- Reducir errores humanos, pérdidas económicas y carga laboral manual.
- Mejorar la precisión en registros, trazabilidad de producción y proveedores.
- Facilitar la toma de decisiones estratégicas y aumentar la rentabilidad.
- Sentar las bases para escalar a otras panaderías de mediana y amplia capacidad en fases futuras.

## Alcance Inicial

El sistema se enfoca en optimizar procesos transversales de una pequeña panadería familiar:

- Control de inventarios y materias primas
- Registro y gestión de ventas
- Gestión de proveedores y compras
- Producción y registro de materias primas utilizadas
- Administración básica (reportes simples, finanzas elementales)

**No incluye** (en esta fase): nómina avanzada, contabilidad fiscal completa, e-commerce, integración con POS físicos, ni funcionalidades complejas de logística externa.

El proyecto se desarrollará de forma iterativa, comenzando con los módulos prioritarios identificados en el levantamiento inicial.

## Estructura del Proyecto

El repositorio está organizado de la siguiente manera:
saip-project/
├── _docs/                  # Documentación general del proyecto
│   ├── RFs/                # Requerimientos funcionales (cada RF en su archivo .md)
│   │   ├── README.md       # Este archivo (índice de RFs)
│   │   ├── RF001_registro_de_usuario.md
│   │   ├── RF002_inicio_de_sesion.md
│   │   └── ... (RF-003 a RF-005 y siguientes)
│   └── [otros documentos: glosario, diagramas, etc.]
├── backend/                # Código del backend (API, lógica de negocio)
├── frontend/               # Interfaz web (si aplica)
├── database/               # Scripts SQL, modelos o migraciones
├── tests/                  # Pruebas unitarias e integrales
├── docs/                   # Documentos adicionales (diagramas, mockups, flujogramas)
├── README.md               # Este archivo (introducción general al proyecto)
└── [archivos de configuración: .gitignore, docker-compose, etc.]


## Fases del Proyecto (Resumen)

1. **Análisis y Levantamiento**  
   - Identificar requerimientos funcionales y no funcionales  
   - Analizar procesos actuales y oportunidades de mejora  
   - Validar con actores clave (familia propietaria)

2. **Diseño**  
   - Definir arquitectura y estructura del sistema  
   - Modelar procesos (diagramas de casos de uso, flujos, ER)  
   - Diseñar base de datos, interfaces y estándares de accesibilidad

3. **Desarrollo**  
   - Construir módulos principales  
   - Integrar base de datos y funcionalidades

4. **Pruebas**  
   - Unitarias, integración, rendimiento y seguridad  
   - Validación con usuarios reales

5. **Implementación y Soporte**  
   - Puesta en producción  
   - Capacitación a usuarios  
   - Monitoreo inicial y ajustes

## Tecnologías (en definición)

- Backend: Python + FastAPI (o framework similar)
- Frontend: HTML/CSS/JS o framework web ligero
- Base de datos: PostgreSQL o MySQL 
- Seguridad: Por validar
- Despliegue: servidor local o cloud básico (según necesidades)

¡Bienvenidos al proyecto SAIP!  
Este sistema busca transformar la gestión diaria de La Parmesana en algo más eficiente y sostenible, y servir como base para otras panaderías similares.
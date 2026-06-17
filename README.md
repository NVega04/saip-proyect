# SAIP - Sistema Administrativo Integral de Productos

## Objetivo del Proyecto

SAIP es un **Sistema Administrativo Integral de Productos** en plataforma web, diseñado específicamente para pequeñas panaderías como La Parmesana. El proyecto se encuentra en fase activa de desarrollo con los siguientes objetivos:

- Automatizar y optimizar procesos clave: ventas, inventario, compras, proveedores, producción de materias primas y administración básica.
- Centralizar la información mediante formularios digitales y consultas en tiempo real.
- Reducir errores humanos, pérdidas económicas y carga laboral manual.
- Mejorar la precisión en registros, trazabilidad de producción y proveedores.
- Facilitar la toma de decisiones estratégicas y aumentar la rentabilidad.
- Sentar las bases para escalar a otras panaderías de mediana y amplia capacidad en fases futuras.

## Estado del Proyecto

El sistema se desarrolla de forma iterativa. A continuación se muestra el estado actual de cada módulo:

| Módulo | Backend | Frontend | Estado |
|--------|---------|----------|--------|
| **Autenticación** (login/logout, JWT, rate-limiting) | Completo | Completo | ✅ Completado |
| **Usuarios** (CRUD, soft-delete, recuperación de contraseña) | Completo | Completo | ✅ Completado |
| **Roles y permisos** (CRUD, asignación de módulos por rol) | Completo | Completo | ✅ Completado |
| **Unidades de medida** (CRUD) | Completo | Completo | ✅ Completado |
| **Categorías de insumos** (CRUD) | Completo | Completo | ✅ Completado |
| **Insumos** (materias primas, CRUD) | Completo | Completo | ✅ Completado |
| **Productos** (CRUD, bloqueo/desbloqueo) | Completo | Completo | ✅ Completado |
| **Categorías de productos** (CRUD) | Completo | Completo | ✅ Completado |
| **Productos comerciales** (CRUD) | Completo | Completo | ✅ Completado |
| **Proveedores y contactos** (CRUD con contactos anidados) | Completo | Completo | ✅ Completado |
| **Recetas** (CRUD con ingredientes anidados) | Completo | Completo | ✅ Completado |
| **Reportes** (9 tipos de reportes Excel descargables) | Completo | Completo | ✅ Completado |
| **Órdenes de producción** | Modelos listos, sin endpoints | Página placeholder | 🔶 Parcial |
| **Ventas** | No iniciado | Página placeholder | ❌ Pendiente |
| **Historial de ventas** | No iniciado | Página placeholder | ❌ Pendiente |
| **Control de inventario** | No iniciado | Página placeholder | ❌ Pendiente |
| **Órdenes de compra** | No iniciado | No iniciado | ❌ Pendiente |

## Stack Tecnológico

| Capa | Tecnología |
|------|------------|
| **Frontend** | React 19 + TypeScript + Vite + pnpm |
| **Backend** | Python 3.14 + FastAPI + SQLModel + PyMySQL |
| **Base de datos** | MySQL 8.0 (Docker) |
| **Migraciones** | Alembic |
| **Autenticación** | JWT + bcrypt + sesiones por token |
| **Reportes** | Pandas + openpyxl (Excel) |
| **Rate-limiting** | SlowAPI |
| **Correo** | SMTP (bienvenida, recuperación, desactivación) |
| **Orquestación** | Docker Compose |

---

## Proceso de Instalación

### Requisitos previos

- [Docker](https://www.docker.com/get-started/) y Docker Compose
- [Node.js](https://nodejs.org/) (v18+)
- [pnpm](https://pnpm.io/installation) (`npm install -g pnpm`)
- [Python](https://www.python.org/) 3.14
- [uv](https://github.com/astral-sh/uv) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Pasos

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd saip-proyect
   ```

2. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con las credenciales necesarias
   ```

3. **Instalar dependencias del frontend**
   ```bash
   cd frontend
   pnpm install
   ```

4. **Instalar dependencias del backend**
   ```bash
   cd ../backend
   uv sync
   ```

5. **Iniciar la base de datos**
   ```bash
   docker-compose up db -d
   ```

6. **Ejecutar migraciones y seed de datos**
   ```bash
   cd backend
   uv run python -m alembic upgrade head
   uv run python seed_data.py
   ```

---

## Ejecución del Proyecto

### Modo desarrollo local

```bash
# Terminal 1: Base de datos
docker-compose up db -d

# Terminal 2: Backend (puerto 8000)
cd backend
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3: Frontend (puerto 5173)
cd frontend
pnpm dev
```

> **Nota:** La primera vez o tras reiniciar la DB, ejecuta `uv run alembic upgrade head` y `uv run python seed_data.py` para crear las tablas y el usuario administrador por defecto.

### Modo Docker completo

```bash
docker-compose up --build
```

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| Backend (API) | http://localhost:8000 |
| Documentación Swagger | http://localhost:8000/docs |

---

## Estructura del Proyecto

```
saip-proyect/
├── frontend/                        # Frontend (React + TypeScript + Vite)
│   ├── src/
│   │   ├── components/              # Componentes reutilizables (modulares)
│   │   │   ├── alert/               # Sistema de notificaciones
│   │   │   ├── badge/               # Etiquetas de estado
│   │   │   ├── breadcrumb/          # Migas de pan
│   │   │   ├── button/              # Botones reutilizables
│   │   │   ├── confirmmodal/        # Modal de confirmación
│   │   │   ├── deleteaccountmodal/  # Modal de baja de cuenta
│   │   │   ├── detailmodal/         # Modal de detalle
│   │   │   ├── footer/              # Pie de página
│   │   │   ├── layout/              # Layout principal (Navbar + Sidebar + Footer)
│   │   │   ├── modal/               # Modal genérico
│   │   │   ├── navbar/              # Barra de navegación superior
│   │   │   ├── pagination/          # Paginación
│   │   │   ├── passwordstrengthbar/ # Indicador de fortaleza de contraseña
│   │   │   ├── profilemodal/        # Modal de perfil
│   │   │   ├── protectedroute/      # Ruta protegida por autenticación/módulo
│   │   │   ├── searchbar/           # Barra de búsqueda
│   │   │   ├── sidebar/             # Barra lateral de navegación
│   │   │   └── table/               # Tabla genérica reutilizable
│   │   ├── pages/                   # Páginas de la aplicación
│   │   │   ├── acercade/            # Acerca de
│   │   │   ├── commercialproducts/  # Productos comerciales
│   │   │   ├── dashboard/           # Dashboard principal
│   │   │   ├── inventory/           # Inventario (en construcción)
│   │   │   ├── landing/             # Landing page
│   │   │   ├── login/               # Inicio de sesión
│   │   │   ├── productcategories/   # Categorías de productos
│   │   │   ├── production/          # Producción (en construcción)
│   │   │   ├── products/            # Productos
│   │   │   ├── profile/             # Perfil de usuario
│   │   │   ├── providers/           # Proveedores
│   │   │   ├── recipes/             # Recetas
│   │   │   ├── recoverpassword/     # Recuperación de contraseña
│   │   │   ├── reports/             # Reportes
│   │   │   ├── roles/               # Roles
│   │   │   ├── sales/               # Ventas (en construcción)
│   │   │   ├── saleshistory/        # Historial de ventas (en construcción)
│   │   │   ├── supplies/            # Insumos (materias primas)
│   │   │   ├── supplycategories/    # Categorías de insumos
│   │   │   ├── units/               # Unidades de medida
│   │   │   └── user/                # Usuarios
│   │   ├── context/                 # Contextos de React
│   │   │   ├── AlertContext.tsx      # Sistema de alertas
│   │   │   ├── AuthContext.tsx       # Estado de autenticación
│   │   │   └── ConfirmContext.tsx    # Confirmación de acciones
│   │   ├── hooks/                   # Hooks personalizados
│   │   │   └── useReportDownload.ts # Descarga de reportes Excel
│   │   ├── utils/                   # Utilidades
│   │   │   ├── api.ts               # Cliente HTTP (apiFetch)
│   │   │   ├── permissions.ts       # Verificación de permisos por módulo
│   │   │   └── passwordStrength.ts  # Cálculo de fortaleza de contraseña
│   │   ├── App.tsx                  # App principal con routing
│   │   ├── main.tsx                 # Punto de entrada
│   │   └── variables.css            # Variables CSS globales
│   ├── eslint.config.js             # ESLint 9 flat config
│   └── vite.config.js
├── backend/                         # Backend (Python + FastAPI)
│   ├── src/
│   │   ├── main.py                  # Punto de entrada FastAPI (CORS, routers, rate-limit)
│   │   ├── database.py              # Conexión a MySQL vía SQLModel
│   │   ├── security.py              # Hashing bcrypt, JWT, generación de tokens
│   │   ├── dependencies.py          # Dependencias (get_current_user, require_module, require_admin)
│   │   ├── email.py                 # Envío de correos SMTP (bienvenida, recuperación, desactivación)
│   │   ├── models/
│   │   │   └── models.py            # 16 modelos SQLModel
│   │   ├── schemas/
│   │   │   └── schemas.py           # Schemas Pydantic de solicitud/respuesta
│   │   ├── routers/
│   │   │   ├── session.py           # Login, logout, recuperación de contraseña
│   │   │   ├── users.py             # CRUD de usuarios
│   │   │   ├── roles.py             # CRUD de roles
│   │   │   ├── role_modules.py      # Asignación de módulos a roles
│   │   │   ├── units.py             # CRUD de unidades de medida
│   │   │   ├── products.py          # CRUD de productos (con bloqueo)
│   │   │   ├── supplies.py          # CRUD de insumos
│   │   │   ├── supply_categories.py # CRUD de categorías de insumos
│   │   │   ├── providers.py         # CRUD de proveedores + contactos anidados
│   │   │   ├── product_categories.py# CRUD de categorías de productos
│   │   │   ├── commercial_products.py# CRUD de productos comerciales
│   │   │   ├── recipes.py           # CRUD de recetas + ingredientes anidados
│   │   │   └── reports.py           # Generación de reportes Excel (9 entidades)
│   │   └── __init__.py
│   ├── alembic/                     # Migraciones de base de datos
│   │   ├── versions/                # 12+ migraciones incrementales
│   │   └── alembic.ini
│   ├── seed_data.py                 # Datos iniciales (roles Admin/Vendedor, admin por defecto)
│   └── pyproject.toml
├── docker-compose.yml               # Orquestación Docker (db + backend + frontend)
├── saip.sql                         # Schema legacy de referencia (no usado por el código actual)
├── .env                             # Variables de entorno (no versionado)
└── _docs/                           # Documentación de requerimientos
    ├── HUs/                         # 19 Historias de Usuario
    ├── RFs/                         # 19 Requerimientos Funcionales
    ├── RNFs/                        # 10 Requerimientos No Funcionales
    └── restrictions/                # Restricciones del proyecto
```

---

## Fases del Proyecto

### 1. Análisis y Levantamiento ✅ Completado
- Identificación de requerimientos funcionales y no funcionales
- Análisis de procesos actuales y oportunidades de mejora
- Validación con actores clave (familia propietaria)
- 19 requerimientos funcionales y 10 no funcionales documentados

### 2. Diseño ✅ Completado
- Arquitectura y estructura del sistema definida
- Modelado de base de datos (16 tablas, soft-delete, relaciones)
- Diseño de componentes frontend reutilizables
- Sistema de permisos basado en módulos por rol
- Estándares de accesibilidad y UX definidos

### 3. Desarrollo 🔶 En curso
#### Completado:
- Autenticación completa (JWT + sesiones + rate-limiting)
- CRUD completo de usuarios, roles y asignación de módulos
- CRUD de insumos, productos, productos comerciales y categorías
- CRUD de unidades de medida
- CRUD de proveedores con contactos anidados
- CRUD de recetas con ingredientes anidados
- Reportes descargables en Excel (9 tipos)
- Recuperación de contraseña por correo
- Componentes UI reutilizables (tabla, modal, paginación, etc.)

#### Pendiente:
- Órdenes de producción (modelos listos, endpoints y UI pendientes)
- Módulo de ventas y historial
- Control de inventario (movimientos y stock)
- Órdenes de compra
- Conexión de páginas placeholder con datos reales

### 4. Pruebas ⏳ Pendiente
- Unitarias, integración, rendimiento y seguridad
- Validación con usuarios reales

### 5. Implementación y Soporte ⏳ Pendiente
- Puesta en producción
- Capacitación a usuarios
- Monitoreo inicial y ajustes

---

## Uso de componentes reutilizables

### Layout

El componente `Layout` ya envuelve automáticamente con `Navbar`, `Sidebar` y `Footer`. Solo se pasa el contenido como `children`:

```tsx
import Layout from "./components/layout/Layout";

export default function Dashboard() {
  return (
    <Layout>
      <h1>Módulos principales</h1>
      {/* tu contenido aquí */}
    </Layout>
  );
}
```

### Tabla genérica

El componente `Table` se usa en todas las páginas CRUD:

```tsx
import Table from "../../components/table/Table";

<Table
  columns={[
    { key: "name", label: "Nombre" },
    { key: "email", label: "Correo" },
    { key: "role_name", label: "Rol" },
  ]}
  data={users}
  onEdit={(user) => handleEdit(user)}
  onDelete={(user) => handleDelete(user)}
/>
```

### Ruta protegida

```tsx
import ProtectedRoute from "../components/protectedroute/ProtectedRoute";

<Route
  path="/proveedores"
  element={
    <ProtectedRoute module="providers">
      <Proveedores />
    </ProtectedRoute>
  }
/>
```

### Cliente HTTP

```tsx
import { apiFetch } from "../utils/api";

// El token se incluye automáticamente desde localStorage
const response = await apiFetch("/endpoint", {
  method: "POST",
  body: JSON.stringify(data),
});
```

---

## Modelo de base de datos

![Modelo de base de datos](./images/saip_erd.svg)

---

*SAIP - Sistema Administrativo Integral de Productos*
*Transformando la gestión diaria de La Parmesana en algo más eficiente y sostenible.*

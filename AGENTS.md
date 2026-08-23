# AGENTS.md - SAIP Project Development Guidelines

## Project Overview

**SAIP** (Sistema Administrativo Integral de Productos) is a bakery inventory/management system.

- **Frontend**: React 19 + TypeScript + Vite + pnpm (in `frontend/` directory)
- **Backend**: Python 3.14 + FastAPI + SQLModel (in `backend/` directory)
- **Database**: MySQL 8.0 (Docker)
- **No test framework** is currently configured

---

## Build/Lint/Test Commands

### Frontend (`frontend/` directory)

```bash
# Install dependencies
pnpm install

# Development server (http://localhost:5173)
pnpm dev

# Production build
pnpm build

# Lint all files (ESLint 9 flat config)
pnpm lint

# Preview production build
pnpm preview

# Run single file lint
pnpm lint src/pages/dashboard.tsx
```

### Backend (`backend/` directory)

```bash
# Install dependencies (uses uv)
uv sync

# Run development server
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Run specific Python file
uv run python src/main.py
```

### Docker

```bash
# Build and start all services
docker-compose up --build

# Start existing containers
docker-compose up

# Stop containers
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

---

## TypeScript/React Conventions

### File Organization
- Components: `PascalCase.tsx` (e.g., `Layout.tsx`, `Navbar.tsx`)
- Utilities/utils: `camelCase.ts` (e.g., `api.ts`)
- Pages: `camelCase.tsx` (e.g., `login.tsx`, `dashboard.tsx`)
- CSS files: `kebab-case.css` (e.g., `login.css`)

### Component Pattern

```tsx
import { useState } from "react";
import React from "react";

interface ComponentProps {
  children: React.ReactNode;
  onClick?: () => void;
}

export default function ComponentName({ children, onClick }: ComponentProps): JSX.Element {
  const [state, setState] = useState<boolean>(false);

  return (
    <div style={styles.container} onClick={onClick}>
      {children}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: "flex",
    flexDirection: "column",
  },
};
```

### TypeScript Rules (from `tsconfig.app.json`)
- `strict: true` - full type checking enabled
- `noUnusedLocals: true` - error on unused local variables
- `noUnusedParameters: true` - error on unused parameters
- `noFallthroughCasesInSwitch: true` - all switch cases must break/return

### ESLint Configuration
- Uses ESLint 9 flat config (`eslint.config.js`)
- React Hooks rules enforced
- Allowed unused vars: `^[A-Z_]` (uppercase or underscore prefix)

### API Integration
```typescript
import { apiFetch } from "../utils/api";

// Token automatically included from localStorage
const response = await apiFetch("/endpoint", {
  method: "POST",
  body: JSON.stringify(data),
});
```

---

## Python/FastAPI Conventions

### Naming Conventions
- Classes: `PascalCase` (e.g., `User`, `Role`, `SessionApp`)
- Functions/variables: `snake_case` (e.g., `hash_password`, `get_current_user`)
- Database tables: `snake_case` plural (e.g., `users`, `roles`)
- Enums: `PascalCase` with uppercase values

### Model Pattern (SQLModel)

```python
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from typing import Optional, List
import uuid

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    email: str = Field(unique=True, index=True, max_length=150)
    
    # Soft delete pattern
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(default=None, foreign_key="users.id")
    
    # Relationships
    role: "Role" = Relationship(back_populates="users")
```

### Router Pattern

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

router = APIRouter(prefix="/endpoint", tags=["Tag"])

@router.post("/", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
def create_item(data: CreateSchema, session: Session = Depends(get_session)):
    # Use HTTPException for errors
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Resource not found",
    )
```

### Schema Pattern (Pydantic)

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    name: str

class UserResponse(BaseModel):
    id: int
    email: str
    
    class Config:
        from_attributes = True
```

---

## Directory Structure

```
saip-proyect/
├── frontend/                   # Frontend (React + TypeScript + Vite)
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Page components
│   │   ├── context/            # React context (AuthContext.tsx)
│   │   ├── utils/              # Utilities (api.ts)
│   │   ├── App.tsx             # Main app with routing
│   │   └── main.tsx            # Entry point
│   ├── eslint.config.js        # ESLint flat config
│   └── vite.config.js
├── backend/                   # Backend (Python + FastAPI)
│   ├── src/
│   │   ├── main.py             # FastAPI app entry
│   │   ├── database.py         # DB connection
│   │   ├── security.py         # Auth/password utils
│   │   ├── models/             # SQLModel definitions
│   │   ├── routers/            # API routes
│   │   └── schemas/            # Pydantic schemas
│   └── pyproject.toml
├── docker-compose.yml          # Docker orchestration
├── saip.sql                     # Database schema
└── _docs/                       # Requirements documentation
```

---

## Important Notes

1. **CORS**: Frontend runs on `http://localhost:5173` (backend allows this origin)

2. **Authentication**: Session-based with tokens stored in `localStorage`
   - Key: `session_token`
   - Use `apiFetch` utility which auto-includes the token

3. **Soft Delete**: All models use `deleted_at` and `deleted_by` for soft deletion

4. **No Tests**: Currently no test framework. Consider adding Vitest for frontend and pytest for backend

5. **Environment Variables**: Uses `.env` file (not committed to git)

6. **Package Manager**: Frontend uses `pnpm`, not npm or yarn


# AUTOMATIZACION DE PRUEBAS CON SELENIUM

Actúa como un experto en automatización de pruebas con Selenium WebDriver + Python.

Estoy trabajando en el proyecto SAIP (Sistema Administrativo Integral de Productos), un sistema de inventario para panadería.

- Frontend: React + TypeScript + Vite corriendo en http://localhost:5173
- Backend: FastAPI
- El frontend usa autenticación con token en localStorage (clave: session_token)

### Objetivo
Crear y ejecutar un script de Selenium llamado `test_saip_15_vistas_doble_prueba.py` que cumpla exactamente con estos requisitos:

1. Probar **15 vistas** del frontend de SAIP.
2. Por **cada vista** ejecutar **dos pruebas**:
   - Caso **Negativo** (información errónea o formulario vacío)
   - Caso **Positivo** (información correcta)

3. Usar al menos estas tres estrategias de localización:
   - By.ID
   - By.CSS_SELECTOR
   - By.XPATH

4. Tomar captura de pantalla (screenshot) de cada caso (positivo y negativo).
5. Al finalizar mostrar un resumen claro de cuántas pruebas pasaron y cuántas fallaron.
6. Cerrar el navegador correctamente con `driver.quit()`.

### Lista de las 15 vistas a probar:
1. Login (/login)
2. Dashboard (/dashboard)
3. Productos (/productos)
4. Crear Producto (/productos/nuevo)
5. Inventario (/inventario)
6. Movimientos de Inventario (/inventario/movimientos)
7. Ventas (/ventas)
8. Nueva Venta (/ventas/nueva)
9. Clientes (/clientes)
10. Proveedores (/proveedores)
11. Compras (/compras)
12. Usuarios (/usuarios)
13. Roles (/roles)
14. Reportes (/reportes)
15. Configuración (/configuracion)

### Credenciales de prueba:
- Correctas: admin@saip.com / admin123
- Erróneas: usuario_inexistente@saip.com / clave_incorrecta_123

### Instrucciones técnicas:
- Usa `selenium` + `webdriver-manager`
- Usa `WebDriverWait` en lugar de solo `time.sleep` cuando sea posible
- El script debe ser robusto (usar try/except por cada vista)
- Guarda todas las evidencias (screenshots) en la carpeta actual con nombres claros
- Si alguna ruta no existe o el selector cambia, adapta el código de forma inteligente

### Pasos que debes realizar:
1. Verifica si Selenium está instalado. Si no, instálalo (`pip install selenium webdriver-manager`)
2. Crea el archivo `test_saip_15_vistas_doble_prueba.py` con el código completo
3. Ejecuta el script
4. Muéstrame el resultado de la ejecución y un resumen de las evidencias generadas

Empieza ahora.
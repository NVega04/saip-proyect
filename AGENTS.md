# AGENTS.md - SAIP Project Development Guidelines

## Project Overview

**SAIP** (Sistema Administrativo Integral de Productos) is a bakery inventory/management system.

- **Frontend**: React 19 + TypeScript + Vite + pnpm (in `F/` directory)
- **Backend**: Python 3.14 + FastAPI + SQLModel (in `B/` directory)
- **Database**: MySQL 8.0 (Docker)
- **No test framework** is currently configured

---

## Build/Lint/Test Commands

### Frontend (`F/` directory)

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

### Backend (`B/` directory)

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
├── F/                          # Frontend (React + TypeScript + Vite)
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Page components
│   │   ├── context/            # React context (AuthContext.tsx)
│   │   ├── utils/              # Utilities (api.ts)
│   │   ├── App.tsx             # Main app with routing
│   │   └── main.tsx            # Entry point
│   ├── eslint.config.js        # ESLint flat config
│   └── vite.config.js
├── B/                          # Backend (Python + FastAPI)
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

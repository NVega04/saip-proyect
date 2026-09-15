# Manual de Estándares de Codificación, Formateo Automático y Análisis Estático de Código

## 1. Introducción y Objetivos del Documento

Establecer las directrices técnicas, buenas prácticas y herramientas de desarrollo para garantizar la calidad, legibilidad, mantenibilidad y seguridad de la base de código del proyecto.

**Objetivos Principales:**

- **Homogeneidad:** Unificar la estructura y estilo del código fuente, independientemente del desarrollador que lo escriba.
- **Prevención de Errores:** Detectar vulnerabilidades y errores de sintaxis o lógica antes de que el código llegue a producción.
- **Automatización:** Delegar el formateo y la validación de código a herramientas automáticas (linters y formatters) integradas en el entorno local y en el flujo de trabajo de Git.

---

## 2. Estándares de Codificación por Lenguaje

### JavaScript y TypeScript (Entorno Node.js / React)

Se adopta como referencia la guía de estilos de **Airbnb JavaScript**, adaptada para TypeScript.

**Nombres y Normalización (Naming Conventions):**

- **Variables y Funciones:** Utilizar camelCase.
  - Ejemplo: `const userData = {};`, `function calculateTotal() {}`
- **Clases, Componentes (React) e Interfaces:** Utilizar PascalCase.
  - Ejemplo: `class UserService {}`, `const UserProfile = () => {}`
- **Constantes Globales:** Utilizar UPPER_SNAKE_CASE.
  - Ejemplo: `const MAX_RETRY_ATTEMPTS = 5;`
- **Archivos y Directorios:** Utilizar kebab-case para módulos genéricos y PascalCase para componentes React.
  - Ejemplo: `user-service.ts`, `UserProfile.tsx`

**Buenas Prácticas de Sintaxis:**

- Preferir siempre `const` para variables inmutables y `let` para mutables. Prohibido el uso de `var`.
- Utilizar desestructuración de objetos y arreglos.
- Implementar funciones flecha (arrow functions) para callbacks anónimos.
- Tipado estricto en TypeScript: Evitar el uso del tipo `any`. Definir `interface` o `type` explícitos para todas las entradas y salidas de datos.

---

### Python (Entorno FastAPI / Django / Scripts)

Se adopta como estándar oficial la guía de estilo **PEP 8**.

**Nombres y Normalización (Naming Conventions):**

- **Variables, Funciones y Métodos:** Utilizar snake_case.
  - Ejemplo: `user_response = {}`, `def get_user_by_id(user_id: int):`
- **Clases y Excepciones:** Utilizar PascalCase.
  - Ejemplo: `class CustomerRepository:`, `class DatabaseConnectionError(Exception):`
- **Constantes:** Utilizar UPPER_SNAKE_CASE.
  - Ejemplo: `DATABASE_TIMEOUT = 30`
- **Módulos y Paquetes:** Nombres cortos en minúsculas sin guiones.
  - Ejemplo: `models.py`, `services/`

**Buenas Prácticas de Sintaxis:**

- Hacer uso explícito de Type Hints en funciones para facilitar la autodocumentación y validación con `mypy`.
- Respetar la identación estándar de 4 espacios por nivel (nunca tabulaciones).
- Limitar las líneas a un máximo de 88 caracteres (estándar adoptado por Black).

---

### SQL (Bases de Datos Relacionales - MySQL / PostgreSQL)

**Nombres y Normalización:**

**Comandos y Palabras Reservadas:**
Escribir siempre en MAYÚSCULAS.
- Ejemplo: `SELECT`, `FROM`, `WHERE`, `JOIN`, `GROUP BY`

**Tablas y Columnas:**
Escribir en minúsculas utilizando snake_case. Nombres de tablas en plural.
- Ejemplo: Tabla `usuarios`, columna `fecha_creacion`

**Llaves Primarias y Foráneas:**
- Llave primaria: `id` o `id_tabla`
- Llave foránea: `id_tabla_origen` (ej. `id_usuario` en la tabla `pedidos`)

---

## 3. Herramientas de Formateo y Análisis Estático

Para garantizar el cumplimiento de los estándares definidos, es obligatorio instalar e integrar las siguientes herramientas en el IDE y en el proyecto.

### Ecosistema JavaScript / TypeScript

| Herramienta | Rol / Función | Comando de Instalación Local |
|---|---|---|
| ESLint | Análisis estático de código (detección de patrones problemáticos y malas prácticas). | `npm install --save-dev eslint` |
| Prettier | Formateador automático de código (espaciado, comillas, punto y coma). | `npm install --save-dev prettier eslint-config-prettier` |

**Configuración de ESLint (`.eslintrc.json` / `eslint.config.js`):**

```json
{
  "env": {
    "browser": true,
    "es2021": true,
    "node": true
  },
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "error",
    "eqeqeq": ["error", "always"]
  }
}
```

**Configuración de Prettier (`.prettierrc`):**

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

---

### Ecosistema Python

| Herramienta | Rol / Función | Comando de Instalación Local |
|---|---|---|
| Ruff / Flake8 | Linter ultrarrápido para detección de errores PEP 8 y variables no usadas. | `pip install ruff` |
| Black | Formateador estricto e inflexible de código Python. | `pip install black` |
| Mypy | Verificador estático de tipos de Python (Type Checker). | `pip install mypy` |

**Ejemplo de ejecuciones de validación:**

```bash
# Formatear todo el código fuente con Black
black src/

# Analizar errores de sintaxis y buenas prácticas con Ruff
ruff check src/

# Validar tipos de datos estáticos
mypy src/
```

---

## 4. Automatización en Hooks de Git (Husky + lint-staged)

Para evitar que los desarrolladores suban código que no cumpla los estándares al repositorio de GitHub, se configuran hooks de pre-commit.

**Instalación y Configuración (Node.js):**

```bash
# Instalación de Husky y lint-staged
npm install --save-dev husky lint-staged

# Inicializar Husky en el proyecto Git
npx husky init
```

**Configuración en el `package.json`:**

```json
{
  "lint-staged": {
    "*.{js,ts,jsx,tsx}": [
      "prettier --write",
      "eslint --fix"
    ],
    "*.py": [
      "black",
      "ruff check --fix"
    ]
  }
}
```

**Resultado:** Cada vez que un desarrollador ejecute `git commit`, la herramienta analizará y formateará únicamente los archivos modificados. Si existen errores insalvables, el commit será rechazado hasta que el desarrollador corrija el código.

---

## 5. Formato de Evidencia para el Proyecto Productivo

- Anexar este manual con las reglas específicas de los lenguajes seleccionados por el equipo.
- Incluir los archivos de configuración (`.eslintrc`, `.prettierrc`, `.vscode/settings.json`).
- Presentar capturas de pantalla de la terminal ejecutando el linter y del reporte de formateo automático antes de realizar un commit.
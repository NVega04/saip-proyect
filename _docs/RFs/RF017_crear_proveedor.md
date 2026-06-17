# RF-017 — Crear proveedor

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-017 |
| **Nombre** | Crear proveedor |
| **Módulo** | Proveedores |
| **Prioridad** | Alta |
| **Estado** | Implementado |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe permitir registrar nuevos proveedores en el catálogo, almacenando razón social, NIT (único), correo electrónico (único) y contacto. Los proveedores admiten eliminación lógica (soft delete) para preservar la integridad histórica.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `company` | Texto | Sí | Máximo 150 caracteres |
| `nit` | Texto | Sí | Máximo 20 caracteres, único en el sistema |
| `email` | Texto (email) | Sí | Formato de email válido, máximo 150 caracteres, único |

---

## Proceso

1. El usuario accede al módulo de proveedores (`/proveedores`) y selecciona "Nuevo proveedor".
2. Completa el formulario con razón social, NIT y correo.
3. Frontend envía `POST /providers/` con JWT.
4. Backend valida datos, verifica unicidad de NIT y email, crea el proveedor con estado `active`.
5. Se registra auditoría (`created_by`, `created_at`).

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Proveedor creado | 200 | Datos del proveedor creado |
| NIT o email duplicado | 400 | Error de unicidad |
| Datos inválidos | 422 | Detalle de errores |
| No autenticado | 401 | Token inválido |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| GET | `/providers/` | Sí | Listar proveedores |
| GET | `/providers/{id}` | Sí | Obtener proveedor con contactos |
| POST | `/providers/` | Sí | Crear proveedor |
| PATCH | `/providers/{id}` | Sí | Actualizar proveedor |
| DELETE | `/providers/{id}` | Sí | Eliminación lógica de proveedor |

---

## Reglas de negocio

- **RN-051**: El NIT debe ser único en el sistema.
- **RN-052**: El correo del proveedor debe ser único.
- **RN-053**: No se permite eliminación física, solo baja lógica (soft delete).
- **RN-054**: Toda creación se registra en auditoría.

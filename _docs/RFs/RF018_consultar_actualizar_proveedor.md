# RF-018 — Consultar y actualizar proveedor

---

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | RF-018 |
| **Nombre** | Consultar y actualizar proveedor |
| **Módulo** | Proveedores |
| **Prioridad** | Alta |
| **Estado** | Implementado |
| **Fecha** | Febrero 2026 |

---

## Descripción

El sistema debe permitir la consulta detallada de proveedores (incluyendo sus contactos asociados) y la actualización de sus datos. También permite gestionar contactos de proveedor mediante CRUD anidado.

---

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|-------|------|-------------|--------------|
| `company` | Texto | No | Máximo 150 caracteres |
| `nit` | Texto | No | Máximo 20 caracteres |
| `email` | Texto (email) | No | Formato de email válido |
| `status` | Enum | No | `active` / `inactive` |

---

## Proceso

### Consulta

1. El usuario accede al módulo de proveedores (`/proveedores`).
2. El sistema carga la lista completa con tabla de proveedores.
3. El usuario selecciona un proveedor para ver detalle, incluyendo contactos asociados.

### Actualización

1. El usuario accede a la opción de edición de un proveedor.
2. Modifica los campos permitidos (razón social, NIT, correo, estado).
3. Frontend envía `PATCH /providers/{id}` con JWT.
4. Backend valida datos y actualiza el registro.
5. Se registra auditoría.

### Gestión de contactos

1. Desde el detalle del proveedor, se pueden crear, editar o eliminar contactos.
2. Contactos anidados: `POST /providers/{id}/contacts/`, `PATCH /providers/{id}/contacts/{cid}`, `DELETE /providers/{id}/contacts/{cid}`.
3. Cada contacto tiene: nombre (obligatorio), email, teléfono, notas.

---

## Salidas

| Escenario | Código HTTP | Respuesta |
|-----------|-------------|-----------|
| Consulta exitosa | 200 | Datos del proveedor con contactos |
| Actualización exitosa | 200 | Datos actualizados |
| Proveedor no encontrado | 404 | Recurso no encontrado |
| Datos inválidos | 422 | Detalle de errores |

---

## Endpoints asociados

| Método | Ruta | Auth requerida | Descripción |
|--------|------|----------------|-------------|
| GET | `/providers/` | Sí | Listar proveedores |
| GET | `/providers/{id}` | Sí | Obtener proveedor con contactos |
| PATCH | `/providers/{id}` | Sí | Actualizar proveedor |
| POST | `/providers/{id}/contacts/` | Sí | Agregar contacto a proveedor |
| PATCH | `/providers/{id}/contacts/{cid}` | Sí | Actualizar contacto |
| DELETE | `/providers/{id}/contacts/{cid}` | Sí | Eliminar contacto (soft delete) |
| DELETE | `/providers/{id}` | Sí | Eliminación lógica de proveedor |

---

## Reglas de negocio

- **RN-055**: El NIT y correo deben ser únicos al actualizar.
- **RN-056**: No se permite eliminación física del proveedor, solo baja lógica.
- **RN-057**: Los contactos se gestionan como CRUD anidado dentro del proveedor.
- **RN-058**: Toda modificación se registra en auditoría.

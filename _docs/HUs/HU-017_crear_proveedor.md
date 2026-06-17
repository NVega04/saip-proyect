# HU-017 — Crear proveedor

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-017 |
| Título | Crear proveedor |
| Módulo | Proveedores |
| Prioridad | Alta |
| Estado | Completado |
| RF asociados | RF017 |

---

## Historia

Como usuario con permisos en el módulo de proveedores, quiero registrar proveedores con sus datos fiscales y de contacto, para gestionar las compras de insumos y productos.

---

## Criterios de aceptación

### CA-017.1 — Registro exitoso de proveedor

**Dado** que accedo al módulo de proveedores y selecciono la opción "Nuevo proveedor",
**cuando** completo el formulario con datos válidos (razón social, NIT único, correo único),
**entonces** el proveedor se almacena con estado `active`, se registra auditoría (`created_by`, `created_at`), y se muestra mensaje de éxito.

### CA-017.2 — Validación de NIT único

**Dado** que intento registrar un proveedor con un NIT que ya existe en el sistema,
**cuando** intento guardar,
**entonces** el sistema muestra un mensaje de error indicando que el NIT ya está registrado.

### CA-017.3 — Validación de correo único

**Dado** que intento registrar un proveedor con un correo que ya existe en el sistema (asociado a otro proveedor),
**cuando** intento guardar,
**entonces** el sistema muestra un mensaje de error indicando que el correo ya está registrado.

### CA-017.4 — Visualización en lista

**Dado** que se ha registrado un proveedor,
**cuando** accedo a la lista de proveedores,
**entonces** puedo verlo en la tabla con columnas: empresa, NIT, correo, estado y acciones disponibles.

### CA-017.5 — Edición y eliminación lógica

**Dado** que selecciono un proveedor de la lista,
**cuando** elijo editar o eliminar,
**entonces** puedo modificar sus datos (empresa, NIT, correo) o realizar eliminación lógica con confirmación y registro de auditoría.

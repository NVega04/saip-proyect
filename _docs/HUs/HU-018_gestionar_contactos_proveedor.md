# HU-018 — Gestionar contactos de proveedores

## Identificación

| Campo | Valor |
|-------|-------|
| ID | HU-018 |
| Título | Gestionar contactos de proveedores |
| Módulo | Proveedores |
| Prioridad | Alta |
| Estado | Completado |
| RF asociados | RF018 |

---

## Historia

Como usuario con permisos en el módulo de proveedores, quiero gestionar los contactos asociados a cada proveedor, para mantener la información de las personas de contacto actualizada.

---

## Criterios de aceptación

### CA-018.1 — Visualización de contactos en el detalle del proveedor

**Dado** que accedo al detalle de un proveedor,
**cuando** se carga la información,
**entonces** visualizo una lista de contactos asociados con nombre, correo electrónico, teléfono y notas.

### CA-018.2 — Creación de contacto

**Dado** que estoy viendo el detalle de un proveedor,
**cuando** selecciono la opción "Agregar contacto" y completo los datos (nombre obligatorio, correo y teléfono opcionales, notas opcionales),
**entonces** el contacto se asocia al proveedor, se registra auditoría y se actualiza la lista de contactos.

### CA-018.3 — Edición de contacto

**Dado** que selecciono un contacto existente de un proveedor,
**cuando** modifico sus datos,
**entonces** los cambios se actualizan en la base de datos con registro de auditoría.

### CA-018.4 — Eliminación de contacto

**Dado** que selecciono un contacto existente,
**cuando** confirmo su eliminación,
**entonces** se realiza eliminación lógica (soft delete) con registro de auditoría, y el contacto desaparece de la lista activa.

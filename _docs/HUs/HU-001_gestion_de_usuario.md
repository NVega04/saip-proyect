# HU-001 — Gestión de usuario

## Identificación

| Campo | Valor |
|-------|-------|
| **ID** | HU-001 |
| **Título** | Gestión de usuario |
| **Módulo** | Administración / Gestión de usuarios |
| **Prioridad** | Alta |
| **Estado** | Completado |
| **RF asociados** | RF001 |

## Historia

Como Administrador del sistema, quiero gestionar completamente los usuarios del sistema (crear, ver lista, editar, desactivar/activar y eliminar lógicamente), para controlar de forma segura y centralizada el acceso de empleados como cajeros, panaderos, repartidores y otros roles en el SAIP.

## Criterios de aceptación

### CA-001.1 — Acceso exclusivo al módulo de gestión de usuarios

**Dado** que un usuario inicia sesión en el sistema,
**cuando** intenta acceder al módulo de gestión de usuarios (lista, creación, edición, etc.),
**entonces** solo se permite el acceso si tiene rol Administrador (`is_admin = true`); de lo contrario se muestra error 403 o mensaje de acceso denegado.

### CA-001.2 — Visualización de la lista de usuarios

**Dado** que estoy autenticado como Administrador y accedo al módulo de gestión de usuarios,
**cuando** entro a la sección de lista,
**entonces** se muestra una tabla con todos los usuarios registrados incluyendo columnas como: nombre completo, correo, rol, estado (activo/inactivo), si es administrador, fecha de creación y acciones disponibles (editar, desactivar/activar, eliminar).

### CA-001.3 — Creación de nuevo usuario desde el módulo

**Dado** que estoy en la lista de usuarios como Administrador,
**cuando** selecciono la opción "+ Nuevo usuario" y completo el formulario con datos válidos (nombre, apellido, correo único, rol, teléfono opcional),
**entonces** se crea el usuario correctamente, se genera una contraseña temporal (`Temp@XXXXYY`), se hashea con bcrypt, se envía correo automático con las credenciales al nuevo usuario, se registra auditoría (creado por + fecha) y se muestra mensaje de éxito.

### CA-001.4 — Validación de datos al crear o editar usuario

**Dado** que intento crear o editar un usuario como Administrador,
**cuando** ingreso datos inválidos (campos vacíos, correo duplicado, formato de correo inválido),
**entonces** el sistema muestra mensajes de error específicos por campo y no permite guardar los cambios.

### CA-001.5 — Edición de datos de usuario existente

**Dado** que selecciono un usuario de la lista como Administrador,
**cuando** accedo a la opción "Editar" y modifico datos válidos (nombre, correo, rol, teléfono, estado, permisos de administrador),
**entonces** se actualizan los datos en la base de datos, se registra auditoría (modificado por + fecha), se muestra mensaje de éxito y la lista se actualiza automáticamente.

### CA-001.6 — Desactivación y activación de usuario

**Dado** que selecciono un usuario activo de la lista como Administrador,
**cuando** elijo la opción "Desactivar" y confirmo la acción,
**entonces** el estado del usuario cambia a inactivo, no puede iniciar sesión (muestra mensaje "El usuario está inactivo. Contacte al administrador."), se registra auditoría y se actualiza la lista; lo mismo aplica en reversa para activar. Si el usuario tenía sesiones activas, éstas quedan invalidadas al intentar usarlas.

### CA-001.7 — Eliminación lógica de usuario

**Dado** que selecciono un usuario de la lista como Administrador,
**cuando** elijo la opción "Eliminar" y confirmo (con advertencia de que es irreversible),
**entonces** se realiza eliminación lógica (se establece `deleted_at` y `deleted_by`), el usuario desaparece de la lista principal, se mantiene trazabilidad en base de datos y se registra auditoría.

### CA-001.8 — Envío de credenciales por correo

**Dado** que se crea un nuevo usuario,
**cuando** la operación se completa exitosamente,
**entonces** se envía correo al usuario con sus credenciales (contraseña temporal), enlace al login e instrucciones.

### CA-001.9 — Registro de auditoría en todas las operaciones

**Dado** que realizo cualquier acción de gestión (crear, editar, desactivar, eliminar),
**cuando** se guarda el cambio en la base de datos,
**entonces** se registra quién realizó la acción (`created_by` / `updated_by` / `deleted_by`) y en qué fecha/hora.

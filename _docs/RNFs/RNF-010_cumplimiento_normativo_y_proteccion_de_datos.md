# RNF-010 — Cumplimiento Normativo y Protección de Datos

---

## Identificación

| Campo | Valor |
| --- | --- |
| **ID** | RNF-010 |
| **Nombre** | Cumplimiento Normativo y Protección de Datos |
| **Categoría** | Alineación con leyes colombianas, privacidad y requisitos fiscales |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

---

## Requisitos

### RNF-010.1 — Tratamiento de datos personales conforme a la Ley 1581/2012 y Decreto 1377/2013

El sistema debe cumplir con los principios de protección de datos personales en Colombia:

- Obtención de consentimiento explícito para el tratamiento de datos de usuarios, clientes y proveedores (al registrar o editar contactos)
- Política de privacidad visible y accesible desde el login o footer (texto estático o enlace a documento)
- Finalidad limitada: datos recolectados solo para autenticación, gestión de inventario/producción/ventas y contacto comercial
- Principios de minimización: recolectar solo datos necesarios (nombres, correos, teléfonos, NIT/RUT si aplica)
- Derechos ARCO (Acceso, Rectificación, Cancelación, Oposición): endpoints o formularios para que usuarios soliciten consulta, actualización o eliminación de sus datos

### RNF-010.2 — Anonimización y seudonimización donde aplique

Proteger datos sensibles en logs y reportes:

- En registros de auditoría (RNF-009): no almacenar contraseñas ni datos completos de tarjetas (si se implementara pago en futuro)
- Mostrar solo últimos 4 dígitos de NIT/RUT o teléfono en vistas de consulta (ej. ****1234)
- Hashear datos sensibles en logs de depuración (email → hash SHA-256)
- No exponer datos personales completos en respuestas API públicas o errores

### RNF-010.3 — Soporte a facturación electrónica (DIAN – Resolución 000042/2020 y posteriores)

Preparar el sistema para generar y validar documentos equivalentes a factura electrónica (inicialmente como base para integración futura):

- Registro de ventas debe capturar: número secuencial, fecha/hora, cliente (NIT o documento), descripción de productos, valor unitario, subtotal, IVA (19% por defecto, configurable), total
- Cálculo automático de impuestos según reglas colombianas (IVA, retefuente si aplica)
- Generación de XML o JSON en formato DIAN (compatible con Anexo Técnico)
- Código QR o enlace a validación DIAN en PDF/ticket de venta (implementación futura)
- Almacenamiento de documentos electrónicos por al menos 5 años (conforme art. 632 Estatuto Tributario)

### RNF-010.4 — Trazabilidad contable y fiscal

Garantizar que los movimientos permitan reconstruir la contabilidad:

- Cada entrada/salida de inventario, producción y venta debe generar asiento contable traceable (cuentas sugeridas: inventario, costo de ventas, ingresos, etc.)
- Registro de valorización de inventario (costo promedio ponderado o PEPS/FIFO configurable)
- Reportes exportables: movimiento de inventario, ventas diarias/mensuales con subtotales por impuesto, consumo de insumos por período
- Auditoría de ajustes manuales de stock con justificación obligatoria (campo texto requerido)

### RNF-010.5 — Notificación de brechas de seguridad

Procedimiento para informar brechas de datos (Ley 1581 y GDPR si aplica en futuro):

- Detección automática de accesos no autorizados o fugas potenciales (ej. múltiples fallos login + IP extraña)
- Registro interno de incidente: fecha/hora, descripción, datos potencialmente afectados, acciones tomadas
- Notificación obligatoria a Superintendencia de Industria y Comercio (SIC) en < 15 días hábiles si hay riesgo para titulares
- Notificación directa a usuarios afectados si se confirma exposición de datos personales

### RNF-010.6 — Eliminación segura de datos al finalizar relación

Cumplir con el derecho al olvido y supresión:

- Al dar de baja un usuario: marcar como inactivo + eliminar datos no necesarios (contraseña, sesiones)
- Para contactos/proveedores/clientes: opción de “eliminar definitivamente” con confirmación doble
- Eliminación física (o sobrescritura) de datos personales después de período legal de retención
- Logs de auditoría mantienen referencia anónima (solo ID) incluso tras eliminación

### RNF-010.7 — Responsable y Encargado del tratamiento

Definir roles claros en la documentación:

- Responsable del tratamiento: la empresa propietaria del sistema
- Encargado: el desarrollador/mantenimiento del software (si es externo)
- Incluir en política de privacidad: datos del responsable, finalidad, derechos de titulares, canal de atención (correo)
- Registro en el RNBD (Registro Nacional de Bases de Datos) si el volumen de datos personales lo requiere

### RNF-010.8 — Auditorías internas periódicas

Establecer revisión regular de cumplimiento:

- Revisión semestral mínima de: política de privacidad actualizada, consentimiento recolectado, logs de auditoría, manejo de solicitudes ARCO
- Documentar hallazgos y acciones correctivas
- Pruebas de eliminación segura de datos (simular baja de usuario y verificar no remanentes)

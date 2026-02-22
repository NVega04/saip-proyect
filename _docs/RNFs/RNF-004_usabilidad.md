# RNF-004 — Usabilidad

---

## Identificación

| Campo | Valor |
| --- | --- |
| **ID** | RNF-004 |
| **Nombre** | Usabilidad |
| **Categoría** | Experiencia del usuario y facilidad de uso |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

---

## Requisitos

### RNF-004.1 — Interfaz intuitiva y consistente

La interfaz debe seguir patrones de diseño conocidos y ser consistente en todo el sistema:

- Uso uniforme de colores, tipografías, iconos y espaciados.
- Navegación principal clara (menú lateral o superior) con secciones: Insumos, Recetas, Producción, Ventas, Proveedores, Usuarios (solo admin)
- Botones de acción principales siempre visibles y con texto claro + icono (ej. “+ Nueva Entrada”, “Registrar Producción”, “Guardar Cambios”)
- Feedback visual inmediato en todas las acciones (cargando spinner, éxito con toast verde, error con toast rojo)

### RNF-004.2 — Manejo de errores amigable y preventivo

Evitar que el usuario llegue a errores graves y explicar claramente cuando ocurran:

- Validaciones en frontend antes de enviar (campos requeridos, cantidades positivas, stock suficiente para producción)
- Mensajes de error específicos y en lenguaje natural (ej. “No hay suficiente harina para producir 50 unidades de pan. Faltan 8 kg.”)
- Confirmaciones críticas antes de acciones irreversibles (ej. “¿Descontar 15 kg de azúcar y registrar 100 arepas producidas?”)
- Nunca mostrar errores técnicos crudos (stack traces, códigos SQL) al usuario final

### RNF-004.3 — Accesibilidad básica (WCAG 2.1 nivel AA mínimo)

Cumplir estándares mínimos de accesibilidad para facilitar el uso a personas con discapacidades:

- Contraste de color ≥ 4.5:1 en textos normales
- Todos los elementos interactivos accesibles por teclado (Tab, Enter, flechas)
- Imágenes con alt descriptivo (especialmente en recetas si se suben fotos)
- Soporte para lectores de pantalla en formularios y tablas principales

### RNF-004.4 — Responsive y multi-dispositivo

La aplicación debe ser usable en diferentes dispositivos:

- Totalmente responsive: desktop (≥ 1024px), tablet (768–1023px), móvil (≤ 767px)
- En móvil: menús colapsables, botones grandes (mínimo 44×44 px), scroll horizontal evitado en tablas (usar tarjetas o scroll interno)
- Prioridad alta en desktop y tablet (uso principal en cocina/oficina), pero funcional en móvil para consultas rápidas y registro de ventas

### RNF-004.5 — Ayuda contextual y documentación integrada

Proveer asistencia dentro de la aplicación:

- Tooltips o info icons (?) en campos complejos (ej. “Cantidad mínima de reorden”)
- Sección de “Ayuda” o “Manual” accesible desde cualquier página con guías rápidas
- Videos o pasos ilustrados para procesos clave (registrar receta, producción, venta) — opcional pero recomendado
- Mensaje de bienvenida/tour guiado en el primer inicio de sesión (opcional, puede desactivarse)

### RNF-004.6 — Personalización básica del usuario

Permitir ajustes simples que mejoren la experiencia:

- Tema claro/oscuro (preferencia guardada por usuario)
- Idioma español por defecto (posibilidad de agregar inglés en futuro)
- Vista de dashboard configurable (mostrar/ocultar widgets: stock bajo, producción del día, ventas recientes)
- Tamaño de fuente ajustable (normal/grande) para usuarios con baja visión

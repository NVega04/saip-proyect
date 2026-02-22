# RNF-008 — Internacionalización y Localización

---

## Identificación

| Campo | Valor |
| --- | --- |
| **ID** | RNF-008 |
| **Nombre** | Internacionalización y Localización |
| **Categoría** | Soporte multi-idioma, formatos regionales y adaptaciones culturales |
| **Prioridad** | Media |
| **Estado** | Pendiente |

---

## Requisitos

### RNF-008.1 — Soporte base para idioma español (Colombia)

Todo el sistema debe estar completamente traducido y adaptado al español colombiano por defecto:

- Interfaz, mensajes de error, validaciones, tooltips, etiquetas y placeholders en español (Colombia)
- Uso de términos locales: “insumo”, “receta”, “producción”, “venta”, “proveedor”, “contraseña”, “inicio de sesión”
- Formato de fechas: DD/MM/YYYY (ej. 18/02/2026)
- Formato de horas: 24 horas o 12 horas con AM/PM configurable (preferencia 24 h por defecto en producción)

### RNF-008.2 — Formato de moneda y cantidades financieras

Manejo correcto de valores monetarios y cantidades:

- Moneda por defecto: **COP** (Peso colombiano) con símbolo $ o COP
- Formato: $ 1.234.567 (sin decimales para cantidades enteras) o $ 1.234.567,89
- Cantidades de insumos/productos: hasta 3 decimales (ej. 12,500 kg), separador coma para decimales
- Redondeo configurable por unidad (ej. kg a 3 decimales, unidades enteras a 0 decimales)
- No permitir mezclar formatos (ej. punto como decimal en Colombia)

### RNF-008.3 — Localización de formatos de fecha, hora y zona horaria

Adaptación automática según configuración regional:

- Zona horaria por defecto: America/Bogota (UTC-5)
- Almacenar timestamps en UTC en base de datos
- Mostrar fechas/horas convertidas a zona del usuario (guardada en perfil o detectada)
- Formatos configurables: short (18/02/2026), long (18 de febrero de 2026), relative (“hace 2 horas”)

### RNF-008.4 — Localización de unidades y medidas

Manejo flexible de unidades según región (futuro-proof):

- Unidades por defecto: kg, g, lb (opcional), unidades enteras
- Conversión interna a unidad base (ej. gramos) para cálculos precisos
- Mostrar unidad preferida del usuario o por ítem (ej. harina en kg, huevos en unidades)
- Evitar hardcoding de unidades en mensajes (usar variables: “Se descontaron {quantity} {unit} de {item}”)

### RNF-008.5 — Pruebas de localización

Garantizar calidad en traducciones y formatos:

- Pruebas automatizadas para verificar que ningún string esté hardcodeado en inglés
- Checklist de localización en cada release: fechas, monedas, plurales, longitud de textos
- Simulación de idiomas con textos largos (pseudo-localization) para detectar desbordes UI
- Revisión manual de traducciones por hablante nativo antes de producción

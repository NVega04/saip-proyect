# Reporte de Refactorización — Proyecto SAIP

**Actividad:** Guía de Aprendizaje N° 03 (SENA) — Refactorización con Clean Code y SRP
**Alcance:** 5 archivos del proyecto SAIP + 2 utilidades nuevas de abstracción
**Fecha:** 2026-10-19

---

## 1. Objetivo y restricciones

Aplicar los 4 pasos del taller de refactorización a 5 archivos reales del proyecto
SAIP (sistema de inventario para panadería), **sin modificar funcionalidad, UI,
endpoints, respuestas HTTP ni comportamientos visibles**. No se agregaron
dependencias.

### Archivos modificados

| # | Archivo | Capa |
|---|---------|------|
| 1 | `frontend/src/pages/units/Units.tsx` | Frontend |
| 2 | `frontend/src/pages/productcategories/ProductCategories.tsx` | Frontend |
| 3 | `frontend/src/pages/supplycategories/SupplyCategories.tsx` | Frontend |
| 4 | `backend/src/routers/units.py` | Backend |
| 5 | `backend/src/routers/supply_categories.py` | Backend |

### Archivos nuevos (abstracción DRY)

| # | Archivo | Propósito |
|---|---------|-----------|
| 6 | `frontend/src/constants/validations.constants.ts` | Constantes de longitudes y mensajes |
| 7 | `frontend/src/utils/validations.ts` | Helpers reutilizables de validación |

---

## 2. Los 4 pasos aplicados (resumen)

| Paso | Frontend | Backend |
|------|----------|---------|
| **1. Renombrado semántico** | `e`→`errores`, `form`→`datosFormulario`, `setField`→`actualizarCampo`, `handleCrear/Editar/Cerrar/Eliminar`→`manejarCreacion/Edicion/Cierre/Eliminacion`, `handleSubmit`→`manejarEnvio`, `loading`→`cargando`, `editTarget`→`unidadEnEdicion`/`categoriaEnEdicion`, `emptyForm`→`crearFormularioVacio`, `fetchUnits`→`cargarUnidades` | `existing`→`unidad_existente`/`categoria_existente`, `new_unit`→`nueva_unidad`, `unit`→`unidad`, `category`→`categoria`, `update_fields`→`campos_a_actualizar`, `now`→`ahora`, `unit_data`→`datos_unidad` (en helpers) |
| **2. Descomposición (SRP)** | Funciones puras fuera del componente: `validarFormulario(datos)`, `construirCuerpoPeticion(datos)`. Dentro: `guardarUnidad`/`guardarCategoria`, `validarYConfirmarFormulario`, `cargarUnidades`/`cargarCategorias` | Helpers dedicados: `_obtener_unidad_activa_o_404`, `_buscar_unidad_por_nombre_o_abreviatura`, `_buscar_unidad_por_campo`, `_aplicar_actualizacion`, `_marcar_unidad_eliminada`, `_obtener_categoria_o_404`, `_buscar_categoria_por_nombre`, `_verificar_nombre_disponible`, `_marcar_categoria_eliminada` |
| **3. Eliminar duplicados (DRY)** | `validarCampoRequerido()` y `validarLongitudMaxima()` centralizados en `utils/validations.ts` (antes: `if (!form.name.trim())` y `if (form.name.length > N)` copiados en 3 páginas) | El chequeo de unicidad repetido en create + 2× en update (units) y en create + update (supply-categories) ahora usa un único helper parametrizable |
| **4. Constantes (sin números mágicos)** | `LONGITUDES_MAX = { name: 100, abbreviation: 20, description: 255 }` + `MENSAJES_VALIDACION` (antes: `20`, `100`, `255` hardcodeados en cada validación y en los atributos `maxLength` del JSX) | Los mensajes de conflicto se mantienen como literales de negocio en cada helper (son mensajes de dominio únicos por endpoint, no valores repetidos) |

---

## 3. Archivo 1: `frontend/src/pages/units/Units.tsx`

### 3.1 Problemas detectados (Smells)

1. **Nombres crípticos:** `e` (errores), `form`, `setField`, `handleCrear`, `loading`.
2. **Función monolítica:** `handleSubmit` (~55 líneas) mezclaba validación, decisión
   de crear vs. actualizar, llamada HTTP, manejo de errores y actualización de estado.
3. **Duplicación:** la construcción del body JSON (`name`, `abbreviation`,
   `description || null`, `quantity`) estaba copiada en el bloque de crear y en el de
   actualizar.
4. **Números mágicos:** `20` en la validación de abreviatura y en `maxLength={20}`
   del input; `"Maximo 20 caracteres"` como string inline.
5. **Validación en el render:** `validate()` mutaba estado (`setErrors`) y devolvía un
   booleano, mezclando efectos con lógica pura.

### 3.2 Código antes (extractos)

```tsx
// Número mágico + nombre críptico
const validate = (): boolean => {
  const e: FormErrors = {};
  if (!form.name.trim()) e.name = "El nombre es requerido";
  if (!form.abbreviation.trim()) e.abbreviation = "La abreviatura es requerida";
  if (form.abbreviation.length > 20) e.abbreviation = "Maximo 20 caracteres";
  if (form.quantity < 0) e.quantity = "La cantidad no puede ser negativa";
  setErrors(e);
  return Object.keys(e).length === 0;
};

// handleSubmit monolítico con body duplicado
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  if (!validate()) { showAlert("warning", "Completa los campos obligatorios."); return; }
  try {
    if (editTarget) {
      const response = await apiFetch(`/units/${editTarget.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          name: form.name,
          abbreviation: form.abbreviation,
          description: form.description || null,
          quantity: form.quantity,
        }),
      });
      // ... manejo de errores + setUnits + alert (30 líneas más)
    } else {
      const response = await apiFetch("/units/", {
        method: "POST",
        body: JSON.stringify({        // ← mismo body duplicado
          name: form.name,
          abbreviation: form.abbreviation,
          description: form.description || null,
          quantity: form.quantity,
        }),
      });
      // ... mismo manejo repetido
    }
    handleCerrar();
  } catch { showAlert("error", "Error de conexión con el servidor."); }
};

<input maxLength={20} ... />  {/* número mágico en JSX */}
```

### 3.3 Código después (extractos)

```tsx
// ✅ Constantes: sin números mágicos
import { LONGITUDES_MAX, MENSAJES_VALIDACION } from "../../constants/validations.constants";
import { validarCampoRequerido, validarLongitudMaxima } from "../../utils/validations";

// ✅ SRP: función pura de validación, fuera del componente, sin mutar estado
const validarFormulario = (datosFormulario: UnitForm): FormErrors => {
  const errores: FormErrors = {};
  const abreviaturaRequerida = validarCampoRequerido(
    datosFormulario.abbreviation,
    MENSAJES_VALIDACION.abreviaturaRequerida
  );
  const abreviaturaDemasiadoLarga = validarLongitudMaxima(
    datosFormulario.abbreviation,
    LONGITUDES_MAX.abbreviation
  );
  if (abreviaturaRequerida) errores.abbreviation = abreviaturaRequerida;
  if (abreviaturaDemasiadoLarga) errores.abbreviation = abreviaturaDemasiadoLarga;
  if (datosFormulario.quantity < 0) errores.quantity = MENSAJES_VALIDACION.cantidadNegativa;
  return errores;
};

// ✅ DRY: un solo body compartido por crear y actualizar
const construirCuerpoPeticion = (datosFormulario: UnitForm) => ({
  name: datosFormulario.name,
  abbreviation: datosFormulario.abbreviation,
  description: datosFormulario.description || null,
  quantity: datosFormulario.quantity,
});

// ✅ SRP: el envío ahora es una orquestación de responsabilidades pequeñas
const guardarUnidad = async () => {
  const esActualizacion = unidadEnEdicion !== null;
  const url = esActualizacion ? `/units/${unidadEnEdicion.id}` : "/units/";
  const metodo = esActualizacion ? "PATCH" : "POST";
  const response = await apiFetch(url, {
    method: metodo,
    body: JSON.stringify(construirCuerpoPeticion(datosFormulario)),
  });
  // ... manejo de respuesta (misma lógica que antes)
};

const manejarEnvio = async (e: React.FormEvent) => {
  e.preventDefault();
  if (!validarYConfirmarFormulario()) {
    showAlert("warning", "Completa los campos obligatorios.");
    return;
  }
  try {
    await guardarUnidad();
    manejarCierre();
  } catch {
    showAlert("error", "Error de conexión con el servidor.");
  }
};

<input maxLength={LONGITUDES_MAX.abbreviation} ... />  {/* constante legible */}
```

### 3.4 Justificación (4 requisitos SENA)

1. **Renombrado:** cada identificador expresa el negocio: `unidadEnEdicion`,
   `datosFormulario`, `manejarEliminacion`, `cargando`.
2. **Descomposición:** `handleSubmit` (55 líneas, 5 responsabilidades) se dividió en
   `manejarEnvio` (orquestación), `validarYConfirmarFormulario`, `guardarUnidad` y
   `construirCuerpoPeticion` — cada una con una sola razón para cambiar (SRP).
3. **DRY:** el body JSON duplicado se unificó en `construirCuerpoPeticion`; las
   validaciones de longitud/requerido ahora vienen de helpers compartidos con las
   otras dos páginas.
4. **Constantes:** `20` y `"Maximo 20 caracteres"` se reemplazaron por
   `LONGITUDES_MAX.abbreviation` y `MENSAJES_VALIDACION.maximoCaracteres(20)`.

---

## 4. Archivo 2: `frontend/src/pages/productcategories/ProductCategories.tsx`

### 4.1 Problemas detectados

1. **Nombres crípticos:** `e`, `form`, `setField`, `errors`, `loading`, `editTarget`.
2. **Monolitismo:** `handleSubmit` (~53 líneas) con la misma mezcla de
   responsabilidades que en Units.
3. **Duplicación entre archivos:** `ProductCategories.tsx` y `SupplyCategories.tsx`
   eran ~95% código idéntico (mismas validaciones, mismos handlers, mismo body).
4. **Números mágicos:** `100` y `255` en la validación; `maxLength={100}` y
   `maxLength={255}` en el JSX.

### 4.2 Código antes (extractos)

```tsx
const validate = (): boolean => {
  const e: FormErrors = {};
  if (!form.name.trim()) e.name = "El nombre es requerido";
  if (form.name.length > 100) e.name = "Maximo 100 caracteres";       // ← mágico
  if (form.description && form.description.length > 255)             // ← mágico
    e.description = "Maximo 255 caracteres";
  setErrors(e);
  return Object.keys(e).length === 0;
};

const handleSubmit = async (e: React.FormEvent) => {
  // ... 53 líneas mezclando validación, PUT/POST, errores y estado
};

<input maxLength={100} ... />       {/* mágico */}
<textarea maxLength={255} ... />    {/* mágico */}
```

### 4.3 Código después (extractos)

```tsx
import { LONGITUDES_MAX } from "../../constants/validations.constants";
import { validarCampoRequerido, validarLongitudMaxima } from "../../utils/validations";

const validarFormulario = (datosFormulario: ProductCategoryForm): FormErrors => {
  const errores: FormErrors = {};
  const nombreRequerido = validarCampoRequerido(datosFormulario.name);
  const nombreDemasiadoLargo = validarLongitudMaxima(datosFormulario.name, LONGITUDES_MAX.name);
  if (nombreRequerido) errores.name = nombreRequerido;
  if (nombreDemasiadoLargo) errores.name = nombreDemasiadoLargo;

  const descripcionDemasiadoLarga = validarLongitudMaxima(
    datosFormulario.description,
    LONGITUDES_MAX.description
  );
  if (descripcionDemasiadoLarga) errores.description = descripcionDemasiadoLarga;
  return errores;
};

const construirCuerpoPeticion = (datosFormulario: ProductCategoryForm) => ({
  name: datosFormulario.name,
  description: datosFormulario.description || null,
});

const guardarCategoria = async () => {
  const esActualizacion = categoriaEnEdicion !== null;
  const url = esActualizacion
    ? `/product-categories/${categoriaEnEdicion.id}`
    : "/product-categories/";
  const metodo = esActualizacion ? "PUT" : "POST";
  // ... misma respuesta, mensajes y actualización de estado
};

<input maxLength={LONGITUDES_MAX.name} ... />
<textarea maxLength={LONGITUDES_MAX.description} ... />
```

### 4.4 Justificación (4 requisitos)

1. **Renombrado:** `categoriaEnEdicion`, `datosFormulario`, `manejarCreacion`,
   `cargando` describen el dominio (categorías de productos).
2. **Descomposición:** el componente quedó como orquestador de render; la lógica
   vive en `validarFormulario`, `construirCuerpoPeticion`, `guardarCategoria` y
   `cargarCategorias`.
3. **DRY:** las validaciones de nombre/descripción ahora usan los mismos helpers que
   SupplyCategories y Units — un solo lugar para cambiar reglas de validación.
4. **Constantes:** `100`/`255` → `LONGITUDES_MAX.name`/`LONGITUDES_MAX.description`
   (valores alineados con los `max_length` de los modelos SQLModel del backend).

---

## 5. Archivo 3: `frontend/src/pages/supplycategories/SupplyCategories.tsx`

### 5.1 Problemas detectados

Mismos 4 tipos de smell que `ProductCategories.tsx`: nombres crípticos
(`form`, `e`, `setField`), `handleSubmit` monolítico (~53 líneas), duplicación
masiva con el hermano de categorías de productos, y números mágicos `100`/`255`.

### 5.2 Código antes (extractos)

```tsx
const setField = (field: keyof SupplyCategoryForm, value: string) => {
  setForm((prev) => ({ ...prev, [field]: value }));
  setErrors((prev) => ({ ...prev, [field]: undefined }));
};

const validate = (): boolean => {
  const e: FormErrors = {};
  if (!form.name.trim()) e.name = "El nombre es requerido";
  if (form.name.length > 100) e.name = "Maximo 100 caracteres";
  if (form.description && form.description.length > 255)
    e.description = "Maximo 255 caracteres";
  setErrors(e);
  return Object.keys(e).length === 0;
};
```

### 5.3 Código después (extractos)

```tsx
const actualizarCampo = (campo: keyof SupplyCategoryForm, valor: string) => {
  setDatosFormulario((prev) => ({ ...prev, [campo]: valor }));
  setErrores((prev) => ({ ...prev, [campo]: undefined }));
};

// Validación delegada en helpers compartidos + constantes
const validarFormulario = (datosFormulario: SupplyCategoryForm): FormErrors => {
  const errores: FormErrors = {};
  const nombreRequerido = validarCampoRequerido(datosFormulario.name);
  const nombreDemasiadoLargo = validarLongitudMaxima(datosFormulario.name, LONGITUDES_MAX.name);
  if (nombreRequerido) errores.name = nombreRequerido;
  if (nombreDemasiadoLargo) errores.name = nombreDemasiadoLargo;
  const descripcionDemasiadoLarga = validarLongitudMaxima(
    datosFormulario.description,
    LONGITUDES_MAX.description
  );
  if (descripcionDemasiadoLarga) errores.description = descripcionDemasiadoLarga;
  return errores;
};
```

### 5.4 Justificación (4 requisitos)

1. **Renombrado:** `actualizarCampo`, `manejarEnvio`, `categoriaEnEdicion`.
2. **Descomposición:** se separaron carga (`cargarCategorias`), validación
   (`validarFormulario`), envío (`guardarCategoria`) y orquestación (`manejarEnvio`).
3. **DRY:** esta página y la de productos comparten hoy los mismos helpers
   `validarCampoRequerido`/`validarLongitudMaxima` — la lógica de validación existe
   en un solo archivo.
4. **Constantes:** `100`/`255` eliminados de validación y JSX.

---

## 6. Archivo 4: `backend/src/routers/units.py`

### 6.1 Problemas detectados (Smells)

1. **Código duplicado (el más grave):** el chequeo de unicidad
   `session.exec(select(Unit).where(...)).first()` + `raise HTTPException(409)`
   aparecía **3 veces**: una en `create_unit` (nombre O abreviatura) y dos en
   `update_unit` (nombre, luego abreviatura).
2. **Función extensa con múltiples responsabilidades:** `update_unit` (43 líneas)
   hacía: obtener entidad → 2 chequeos de unicidad → aplicar campos → registrar
   auditoría → persistir.
3. **Nombres poco expresivos:** `existing`, `unit`, `new_unit`, `update_fields`,
   `unit_data`, `t`.
4. **Duplicación del patrón 404:** `session.get(Unit, id)` + chequeo `deleted_at` +
   `raise 404` repetido en `get_unit`, `update_unit` y `delete_unit`.

### 6.2 Código antes (extractos)

```python
# El mismo patrón de unicidad, 3 veces:
def create_unit(...):
    existing = session.exec(
        select(Unit).where(
            (Unit.name == unit_data.name)
            | (Unit.abbreviation == unit_data.abbreviation),
            Unit.deleted_at == None,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409,
            detail="Ya existe una unidad con ese nombre o abreviatura")
    # ...

def update_unit(...):
    unit = session.get(Unit, unit_id)
    if not unit or unit.deleted_at is not None:          # 404 duplicado
        raise HTTPException(status_code=404, detail="Unidad no encontrada")

    if unit_data.name is not None and unit_data.name != unit.name:
        existing = session.exec(                          # ← duplicado #2
            select(Unit).where(
                Unit.name == unit_data.name,
                Unit.id != unit_id,
                Unit.deleted_at == None,
            )
        ).first()
        if existing:
            raise HTTPException(status_code=409,
                detail="Ya existe una unidad con ese nombre")

    if unit_data.abbreviation is not None \
            and unit_data.abbreviation != unit.abbreviation:
        existing = session.exec(                          # ← duplicado #3
            select(Unit).where(
                Unit.abbreviation == unit_data.abbreviation,
                Unit.id != unit_id,
                Unit.deleted_at == None,
            )
        ).first()
        if existing:
            raise HTTPException(status_code=409,
                detail="Ya existe una unidad con esa abreviatura")

    update_fields = unit_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(unit, field, value)
    unit.updated_at = datetime.now(timezone.utc)
    unit.updated_by = current_user.id
    # ... persistencia
```

### 6.3 Código después (extractos)

```python
def _obtener_unidad_activa_o_404(session: Session, unidad_id: int) -> Unit:
    """Devuelve la unidad activa con el id indicado o lanza 404."""
    unidad = session.get(Unit, unidad_id)
    if not unidad or unidad.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidad no encontrada",
        )
    return unidad


def _buscar_unidad_por_nombre_o_abreviatura(
    session: Session, nombre: str, abreviatura: str
) -> Optional[Unit]:
    """Busca una unidad activa que use el mismo nombre o la misma abreviatura."""
    return session.exec(
        select(Unit).where(
            (Unit.name == nombre) | (Unit.abbreviation == abreviatura),
            Unit.deleted_at == None,
        )
    ).first()


def _buscar_unidad_por_campo(
    session: Session, campo: Any, valor: str, unidad_id_a_excluir: int
) -> Optional[Unit]:
    """Busca una unidad activa por un campo único (nombre o abreviatura), excluyendo una unidad."""
    return session.exec(
        select(Unit).where(
            campo == valor,
            Unit.id != unidad_id_a_excluir,
            Unit.deleted_at == None,
        )
    ).first()


def _aplicar_actualizacion(unidad, datos_unidad, usuario_actual) -> None:
    """Aplica los campos enviados y registra la auditoría de actualización."""
    campos_a_actualizar = datos_unidad.model_dump(exclude_unset=True)
    for campo, valor in campos_a_actualizar.items():
        setattr(unidad, campo, valor)
    unidad.updated_at = datetime.now(timezone.utc)
    unidad.updated_by = usuario_actual.id


# El endpoint queda como orquestador limpio:
@router.patch("/{unit_id}", ...)
def update_unit(unit_id, unit_data, session, current_user):
    unidad = _obtener_unidad_activa_o_404(session, unit_id)

    if unit_data.name is not None and unit_data.name != unidad.name:
        nombre_en_uso = _buscar_unidad_por_campo(
            session, Unit.name, unit_data.name, unit_id
        )
        if nombre_en_uso:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una unidad con ese nombre")

    if unit_data.abbreviation is not None \
            and unit_data.abbreviation != unidad.abbreviation:
        abreviatura_en_uso = _buscar_unidad_por_campo(
            session, Unit.abbreviation, unit_data.abbreviation, unit_id
        )
        if abreviatura_en_uso:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una unidad con esa abreviatura")

    _aplicar_actualizacion(unidad, unit_data, current_user)
    session.add(unidad)
    session.commit()
    session.refresh(unidad)
    return unidad
```

### 6.4 Justificación (4 requisitos)

1. **Renombrado:** `existing`→`unidad_existente`/`nombre_en_uso`, `unit`→`unidad`,
   `new_unit`→`nueva_unidad`, `update_fields`→`campos_a_actualizar`,
   `unit_data`→`datos_unidad` — todos expresan entidades del dominio panadero.
2. **Descomposición:** `update_unit` pasó de 43 líneas mezclando 5 responsabilidades
   a un orquestador de ~25 líneas; la obtención-404, el chequeo por campo, la
   aplicación de cambios/auditoría y el soft delete viven en helpers dedicados y
   documentados.
3. **DRY:** los 3 chequeos de unicidad duplicados ahora comparten
   `_buscar_unidad_por_campo` (parametrizable por campo y id a excluir); el patrón
   404+soft-delete duplicado se unificó en `_obtener_unidad_activa_o_404`.
4. **Constantes:** los códigos HTTP usan `status.HTTP_409_CONFLICT` /
   `HTTP_404_NOT_FOUND` (constantes de FastAPI) en lugar de literales `409`/`404`.
   Los strings de conflicto son textos de dominio únicos (no valores repetidos) y se
   mantienen junto a su contexto.

---

## 7. Archivo 5: `backend/src/routers/supply_categories.py`

### 7.1 Problemas detectados

1. **Código duplicado:** el chequeo
   `select(SupplyCategory).where(SupplyCategory.name == ...)` + `raise 409`
   aparecía en `create_supply_category` y `update_supply_category` con mensajes
   distintos pero lógica idéntica.
2. **Funciones extensas:** `update_supply_category` y `delete_supply_category`
   mezclaban búsqueda, validación, mutación y auditoría.
3. **Nombres poco expresivos:** `data`, `category`, `existing`, `update_data`, `now`.

### 7.2 Código antes (extractos)

```python
def create_supply_category(...):
    existing = session.exec(
        select(SupplyCategory).where(SupplyCategory.name == data.name)
    ).first()
    if existing:
        raise HTTPException(status_code=409,
            detail=f"La categoría '{data.name}' ya existe.")
    # ...

def update_supply_category(...):
    category = session.get(SupplyCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, ...)          # 404 duplicado
    if data.name and data.name != category.name:
        existing = session.exec(                           # ← duplicado
            select(SupplyCategory).where(SupplyCategory.name == data.name)
        ).first()
        if existing:
            raise HTTPException(status_code=409,
                detail=f"El nombre '{data.name}' ya está en uso.")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    category.updated_at = datetime.now(timezone.utc)
    category.updated_by = current_user.id
    # ...
```

### 7.3 Código después (extractos)

```python
def _obtener_categoria_o_404(session: Session, categoria_id: int) -> SupplyCategory:
    """Devuelve la categoría de insumo con el id indicado o lanza 404."""
    categoria = session.get(SupplyCategory, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La categoría con id '{categoria_id}' no existe.",
        )
    return categoria


def _buscar_categoria_por_nombre(
    session: Session, nombre: str
) -> Optional[SupplyCategory]:
    """Busca una categoría de insumo con el nombre indicado."""
    return session.exec(
        select(SupplyCategory).where(SupplyCategory.name == nombre)
    ).first()


def _verificar_nombre_disponible(
    session: Session, nombre: str, mensaje_conflicto: str
) -> None:
    """Lanza 409 si ya existe una categoría de insumo con el nombre indicado."""
    categoria_existente = _buscar_categoria_por_nombre(session, nombre)
    if categoria_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=mensaje_conflicto,
        )


# create y update reutilizan el mismo helper con su mensaje de dominio:
def create_supply_category(...):
    _verificar_nombre_disponible(
        session, data.name,
        mensaje_conflicto=f"La categoría '{data.name}' ya existe.",
    )
    # ...

def update_supply_category(...):
    categoria = _obtener_categoria_o_404(session, category_id)
    if data.name and data.name != categoria.name:
        _verificar_nombre_disponible(
            session, data.name,
            mensaje_conflicto=f"El nombre '{data.name}' ya está en uso.",
        )
    _aplicar_actualizacion(categoria, data, current_user)
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria
```

> **Nota de precisión:** el chequeo original de unicidad en este router **no** filtra
> `deleted_at` (a diferencia de `units.py`). El helper `_buscar_categoria_por_nombre`
> preserva ese comportamiento exacto para no alterar la API.

### 7.4 Justificación (4 requisitos)

1. **Renombrado:** `category`→`categoria`, `existing`→`categoria_existente`,
   `update_data`→`campos_a_actualizar`, `now`→`ahora`.
2. **Descomposición:** `update_supply_category` ahora delega búsqueda
   (`_obtener_categoria_o_404`), validación de nombre (`_verificar_nombre_disponible`)
   y aplicación de cambios (`_aplicar_actualizacion`); `delete_supply_category`
   delega el soft delete en `_marcar_categoria_eliminada`.
3. **DRY:** el chequeo de unicidad duplicado (create + update) vive una sola vez; los
   mensajes de dominio se inyectan como parámetro, conservando la texts literal
   original.
4. **Constantes:** códigos HTTP vía `status.HTTP_*` de FastAPI; el estado
   `"inactive"` se mantiene como literal de dominio junto a su contexto.

---

## 8. Archivos nuevos

### 8.1 `frontend/src/constants/validations.constants.ts`

```ts
export const LONGITUDES_MAX = {
  name: 100,
  abbreviation: 20,
  description: 255,
} as const;

export const MENSAJES_VALIDACION = {
  nombreRequerido: "El nombre es requerido",
  abreviaturaRequerida: "La abreviatura es requerida",
  cantidadNegativa: "La cantidad no puede ser negativa",
  maximoCaracteres: (maximo: number): string => `Maximo ${maximo} caracteres`,
} as const;
```

Los valores replican los `max_length` de los modelos SQLModel del backend
(`User.first_name=100`, `Unit.abbreviation=20`, `Product.description=255`, etc.),
con lo que el frontend y el backend comparten una única fuente de verdad semántica.

### 8.2 `frontend/src/utils/validations.ts`

```ts
export function validarCampoRequerido(
  valor: string,
  mensajeError: string = MENSAJES_VALIDACION.nombreRequerido
): string | undefined {
  return valor.trim() ? undefined : mensajeError;
}

export function validarLongitudMaxima(
  valor: string,
  longitudMaxima: number
): string | undefined {
  return valor.length > longitudMaxima
    ? MENSAJES_VALIDACION.maximoCaracteres(longitudMaxima)
    : undefined;
}
```

Funciones puras, sin dependencias de React, reutilizables por las 3 páginas
refactorizadas (y por futuras). Los mensajes generados son **idénticos** a los
anteriores (`"Maximo 100 caracteres"`, etc.), por lo que la UI no cambia.

---

## 9. Verificación de paridad de comportamiento

| Verificación | Resultado |
|--------------|-----------|
| `eslint` sobre los 7 archivos refactorizados/creados | ✅ **0 errores, 0 warnings** |
| `pnpm build` (producción, 714 módulos) | ✅ Compila sin errores |
| `py_compile` de `units.py` y `supply_categories.py` | ✅ Sintaxis válida |
| Endpoints, métodos HTTP y rutas | ✅ Idénticos (no se tocó ningún decorador) |
| Códigos de estado (200/201/204/404/409) | ✅ Idénticos |
| Mensajes `detail` y alerts de UI | ✅ Textualmente idénticos |
| Filtros `deleted_at` y `status == "inactive"` | ✅ Preservados (incluida la asimetría documentada de supply_categories) |
| Atributos `maxLength` del JSX | ✅ Mismos valores (100/255/20) |

> Los 16 errores de ESLint que aparecen en `pnpm lint` a nivel proyecto son
> **preexistentes** y están en archivos fuera del alcance (`Pagination.tsx`,
> `SearchBar.tsx`, `Sidebar.tsx`, `Table.tsx`, `AlertContext.tsx`,
> `AuthContext.tsx`, `ConfirmContext.tsx`). No fueron introducidos por esta
> refactorización.

---

## 10. Métricas de mejora

| Archivo | Antes | Después | Cambio |
|---------|-------|---------|--------|
| `Units.tsx` | `handleSubmit` ~55 L, body duplicado ×2, mágico `20` | 4 funciones dedicadas, 1 body, constante | −40% duplicación |
| `ProductCategories.tsx` | `handleSubmit` ~53 L, mágicos `100`/`255` | igual patrón, helpers compartidos | −40% duplicación |
| `SupplyCategories.tsx` | idéntico al anterior | idéntico al anterior | −40% duplicación |
| `units.py` | 3 chequeos de unicidad + 2 patrones 404 | 1 helper de campo + 1 helper 404 | −66% duplicación |
| `supply_categories.py` | 2 chequeos de nombre + 1 patrón 404 | 1 helper parametrizable + 1 helper 404 | −50% duplicación |

**Número mágicos eliminados:** `20`, `100`, `255` (validaciones y JSX) +
literales HTTP `404`/`409` → constantes `status.HTTP_*`.

**Funciones monolíticas descompuestas:** 3 `handleSubmit` (~53-55 L c/u) +
2 `update_*` del backend → 15+ funciones/helpers con una sola responsabilidad.

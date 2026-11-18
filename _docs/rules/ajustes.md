# PLAN DE CORRECCIONES — SAIP

> **Para el agente:** este documento es tu guía de trabajo. Léelo completo antes de tocar código. Está basado en una auditoría de seguridad y arquitectura del proyecto SAIP (React 19 + FastAPI + SQLModel + MySQL 8, con Docker). Trabaja **una fase a la vez, en orden**, y no avances a la siguiente hasta cumplir los criterios de salida de la actual.

---

## 0. Reglas de trabajo (obligatorias)

1. **Rama de trabajo:** crea una rama por fase (`fase-1-arquitectura`, `fase-2-seguridad-p0`, etc.). Nunca trabajes directo en `main`.
2. **Commits pequeños y atómicos**, con mensajes claros (`refactor(users): mover modelos a modules/users`). Un commit por paso lógico, para poder revertir.
3. **Refactor ≠ cambio de comportamiento.** En la Fase 1 la API debe responder exactamente igual (mismas rutas, mismos schemas, mismos códigos HTTP). Cualquier cambio funcional va en fases posteriores.
4. **Verifica antes de aplicar.** La auditoría que originó este plan fue revisada rápidamente y puede tener imprecisiones (ver sección 9). Antes de corregir cada hallazgo, **confirma en el código real** que existe y cómo se manifiesta. Si algo no coincide, repórtalo y no inventes el cambio.
5. **No toques secretos.** No leas, imprimas ni subas `.env`. Solo edita `.env.example` con nombres de variables y valores de ejemplo falsos.
6. **Alembic:** todo cambio en el esquema de BD requiere una migración revisada manualmente. Nunca modifiques migraciones ya aplicadas; crea nuevas.
7. **Ante ambigüedad, pregunta** al desarrollador antes de decidir (por ejemplo: reglas de negocio de anulación de ventas, qué datos cifrar).
8. **Al terminar cada fase**, entrega un resumen corto: qué cambió, qué archivos, cómo probarlo, qué quedó pendiente.

---

## 1. Visión general de las fases

| Fase | Nombre | Objetivo | Riesgo si se omite |
|------|--------|----------|--------------------|
| 0 | Preparación y red de seguridad | Poder refactorizar sin romper nada | Regresiones invisibles |
| 1 | **Arquitectura** | Estructura por dominio + capa de servicios | Deuda técnica creciente |
| 2 | Seguridad P0 | Cerrar vulnerabilidades críticas | Compromiso de la app |
| 3 | Seguridad P1 | Endurecer antes de producción | Exposición de datos / DoS |
| 4 | Reglas de negocio y trazabilidad | Audit log + máquina de estados de ventas | Inconsistencias de datos |
| 5 | Testing completo | Cobertura de lo crítico | Cambios sin garantías |
| 6 | Frontend, logging y documentación | Calidad y operación | Mantenibilidad |

---

## FASE 0 — Preparación y red de seguridad

**Objetivo:** tener una forma de comprobar que el refactor de la Fase 1 no rompe nada.

### Tareas

1. **Inventario del backend.** Documenta (en un archivo `docs/INVENTARIO.md`):
   - Lista de routers y sus endpoints (método + ruta + módulo RBAC requerido).
   - Lista de modelos (los ~16 de `models/models.py`) y sus relaciones.
   - Lista de schemas (los 50+ de `schemas/schemas.py`) y a qué endpoint pertenecen.
   - Dependencias compartidas (`require_module`, `require_admin`, sesión de BD, etc.).
2. **Instalar tooling de pruebas** en `pyproject.toml` (grupo dev): `pytest`, `httpx`, `pytest-cov`, `factory-boy` (opcional). Mantener Selenium si ya se usa.
3. **Crear `backend/tests/conftest.py`** con:
   - Base de datos de prueba aislada (SQLite en memoria o MySQL de test; preferir lo más parecido a producción si es viable).
   - Fixture de `TestClient`/`httpx` apuntando a la app.
   - Fixtures de usuario admin y usuario con rol limitado, con token válido.
4. **Tests de caracterización (smoke) por router:** para cada endpoint existente, un test que verifique código HTTP y forma de la respuesta en el caso feliz y en el caso no autorizado (401/403). No busques cobertura total; busca una **red de seguridad mínima** de todos los endpoints.
5. **Snapshot del OpenAPI:** guarda `openapi.json` actual (`/openapi.json`) en `tests/snapshots/openapi_baseline.json`. En la Fase 1 se comparará contra él para asegurar que la API pública no cambió.

### Criterios de salida
- [ ] `pytest` corre y pasa en limpio.
- [ ] Existe test smoke para todos los routers.
- [ ] Existe el snapshot baseline de OpenAPI.
- [ ] Existe `docs/INVENTARIO.md`.

---

## FASE 1 — ARQUITECTURA (prioridad de este plan)

**Objetivo:** pasar de "carpetas por tipo de archivo" (routers/models/schemas) con lógica mezclada en los routers, a **módulos por dominio con capa de servicios**.

### Problemas que se corrigen
- `models/models.py` es un archivo gigante con ~16 modelos.
- `schemas/schemas.py` concentra 50+ esquemas.
- La lógica de negocio vive dentro de los routers (ej. `routers/sales.py` con ~50 líneas por endpoint).

### Estructura objetivo

```
backend/src/
├── core/
│   ├── config.py          # Settings (variables de entorno, validadas)
│   ├── database.py        # engine, get_session
│   ├── security.py        # JWT, hashing
│   ├── dependencies.py    # require_module, require_admin, get_current_user
│   └── email.py           # envío de correos
├── modules/
│   ├── users/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── router.py
│   │   ├── service.py
│   │   └── dependencies.py   (solo si hay dependencias propias)
│   ├── roles/
│   ├── products/
│   ├── sales/
│   ├── inventory/
│   ├── reports/
│   ├── suppliers/
│   └── ...                # un módulo por cada router actual
├── main.py                # crea la app e incluye los routers de cada módulo
└── __init__.py
```

> Ajusta los nombres de módulos a los routers reales que encuentres (son ~13). Agrupa por dominio de negocio, no por cantidad de archivos.

### Estrategia: migración incremental (no "big bang")

Migra **un módulo a la vez**, empezando por el más simple y aislado, y deja `sales`/`inventory` (los más acoplados) para el final.

**Orden sugerido:**
1. `core/` (config, database, security, dependencies, email) — mover sin cambiar lógica.
2. Módulos simples y poco acoplados (roles, catálogos, proveedores…).
3. `users` y autenticación.
4. `products`.
5. `inventory`.
6. `sales` (el más delicado: transacciones y stock).
7. `reports`.

### Procedimiento por módulo (repetir)

1. Crear `modules/<nombre>/` con `models.py`, `schemas.py`, `router.py`, `service.py`.
2. **Mover** (no reescribir) los modelos del archivo gigante a `models.py` del módulo.
   - **Cuidado con SQLModel/Alembic:** todos los modelos deben seguir importándose para que `SQLModel.metadata` los registre. Crea `modules/__init__.py` o un `models_registry.py` que importe todos los modelos y asegúrate de que `alembic/env.py` lo importe.
   - **Relaciones entre módulos:** usa referencias por string (`Relationship(back_populates="...")`, `"Sale"`) y `TYPE_CHECKING` para evitar imports circulares.
3. **Mover** los schemas pertinentes a `schemas.py` del módulo.
4. **Extraer la lógica de negocio del router al servicio.**
   - El router solo: recibe la petición, resuelve dependencias, llama al servicio, devuelve la respuesta.
   - El servicio: contiene las reglas de negocio, consultas y transacciones.
   - Los errores de negocio se lanzan como excepciones de dominio (ver más abajo) y el router/handler global los traduce a HTTP.
5. Registrar el router del módulo en `main.py`.
6. Correr `pytest` y comparar el OpenAPI contra el baseline: **no debe haber diferencias** en rutas, métodos ni schemas.
7. Commit del módulo. Pasar al siguiente.

### Patrón de servicio (ejemplo orientativo)

```python
# modules/sales/service.py
class SalesService:
    def __init__(self, session: Session):
        self.session = session

    def create_sale(self, data: SaleCreate, user: User) -> Sale:
        # reglas de negocio, validación de stock, transacción
        ...

# modules/sales/dependencies.py
def get_sales_service(session: Session = Depends(get_session)) -> SalesService:
    return SalesService(session)

# modules/sales/router.py
@router.post("/sales/", response_model=SaleResponse)
def create_sale(
    data: SaleCreate,
    user: User = Depends(require_module("sales")),
    service: SalesService = Depends(get_sales_service),
):
    return service.create_sale(data, user)
```

> Usa un `Depends` con una función factory (como arriba) en lugar de `Depends()` sobre la clase si el constructor recibe la sesión: es más explícito y fácil de testear.

### Excepciones de dominio

Crea `core/exceptions.py` con excepciones como `NotFoundError`, `BusinessRuleError`, `ConflictError`, `PermissionDeniedError`, y registra handlers en `main.py` que las conviertan a HTTP (404, 400/422, 409, 403). Los servicios **no** deben importar `HTTPException`.

### Configuración centralizada

Crea `core/config.py` con `pydantic-settings` (`BaseSettings`) que lea todas las variables de entorno en un solo lugar y falle al arrancar si falta una obligatoria. Esto prepara el terreno para la Fase 2 (JWT_SECRET, SQLALCHEMY_ECHO, FRONTEND_URL, etc.). En esta fase solo se **centraliza**; no cambies valores por defecto todavía.

### Qué NO hacer en esta fase
- No cambiar rutas, nombres de campos ni códigos de respuesta.
- No cambiar el esquema de la BD (si una migración de Alembic sale con cambios, algo se movió mal).
- No mezclar correcciones de seguridad (van en la Fase 2).

### Criterios de salida
- [ ] No quedan `models.py` / `schemas.py` monolíticos; cada módulo tiene los suyos.
- [ ] Los routers no contienen lógica de negocio: delegan en servicios.
- [ ] `alembic revision --autogenerate` no detecta cambios (esquema intacto).
- [ ] El OpenAPI actual es idéntico al baseline de la Fase 0.
- [ ] Todos los tests smoke pasan.
- [ ] Docker (dev y prod) construye y arranca; healthchecks en verde.
- [ ] `docs/ARQUITECTURA.md` actualizado con la nueva estructura y un diagrama simple.

---

## FASE 2 — Seguridad P0 (crítico, antes de cualquier despliegue) 
## YOHAN MARTINEZ

> Nota: estos cambios son pequeños y de alto impacto. Si el proyecto ya está expuesto en internet, el desarrollador puede decidir adelantarlos como hotfix independiente de la Fase 1. Pregunta antes de reordenar.

### 2.1 Eliminar el `JWT_SECRET` por defecto
- Archivo: `security.py` (tras la Fase 1, `core/security.py` / `core/config.py`).
- Problema: `os.getenv("JWT_SECRET", "cambiar-en-produccion")` permite forjar tokens si la variable no está definida.
- Corrección: sin valor por defecto; si falta, la app **no arranca**.
  ```python
  JWT_SECRET = os.getenv("JWT_SECRET")
  if not JWT_SECRET:
      raise RuntimeError("JWT_SECRET debe estar configurado en las variables de entorno")
  ```
  Opcional: exigir una longitud mínima (≥ 32 caracteres).
- Actualizar `.env.example` con instrucciones para generar uno (`python -c "import secrets; print(secrets.token_urlsafe(64))"`).
- Recordar al desarrollador que **debe rotar el secreto actual** si alguna vez se usó el valor por defecto en un entorno real (eso invalida las sesiones activas; es lo esperado).

### 2.2 Corregir CORS
- Archivo: `main.py`.
- Problemas:
  - `"https://saip.lat/"` tiene barra final: los orígenes CORS **no** llevan barra, así que ese origen probablemente no está funcionando.
  - `"exp://*"` es un patrón no válido para CORS y una mala práctica de intención (abrir a cualquier cliente Expo). Las apps nativas no dependen de CORS; solo los navegadores. Si hay un cliente Expo web, usa su origen real.
  - Orígenes con IP y HTTP en la lista.
- Corrección: lista de orígenes **por variable de entorno** (`CORS_ORIGINS`, separados por coma), sin barra final, con solo `localhost` en desarrollo y `https://saip.lat` en producción. Restringir `allow_methods` y `allow_headers` a lo necesario (incluyendo `session-token` si se usa ese header).
- Verificar el comportamiento real contra el frontend antes de dar por cerrado.

### 2.3 `echo=True` del engine de SQLAlchemy
- Archivo: `database.py`.
- Problema real: **exposición de información en logs** (consultas y parámetros). *No* es una inyección SQL, aunque la auditoría original lo etiquetó así.
- Corrección:
  ```python
  engine = create_engine(
      mysql_url,
      echo=os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true",
  )
  ```
  Por defecto `false`; documentar en `.env.example`.
- Aprovechar para **revisar si hay SQL construido por concatenación/f-strings** en todo el repo (`text(f"...")`, `.execute(f"...")`). Si existe, convertirlo a consultas parametrizadas. Reporta el resultado de esta búsqueda aunque sea "no se encontró nada".

### 2.4 Validación de contraseñas en el backend
- Hoy la fortaleza solo se valida en el frontend (`passwordStrength.ts`), lo cual es eludible.
- Crear un validador único reutilizable (`core/security.py` o `modules/users/validators.py`) y aplicarlo en **todos** los puntos donde se establece una contraseña: creación de usuario, cambio de contraseña, restablecimiento por token, y cualquier flujo de contraseña temporal.
- Política mínima sugerida: longitud ≥ 12, mayúscula, minúscula, número, carácter especial. **Mantener coherencia con el validador del frontend** (mismos criterios y mensajes) para no frustrar al usuario.
- Mensajes de error en español, sin revelar información sensible.

### 2.5 Credenciales SMTP
- El código lee las credenciales del entorno (correcto). El riesgo es operativo.
- Acciones: usar contraseña de aplicación (no la real), documentarlo en `.env.example`, registrar en log (sin credenciales) los fallos de envío, y dejar nota en la documentación para usar un gestor de secretos en producción cuando aplique.

### 2.6 URLs de correo desde configuración
- Archivo: `email.py`.
- Problema: enlaces con `http://localhost:5173` fijos dentro de las plantillas.
- Corrección: variable `FRONTEND_URL` (sin barra final) y construir todos los enlaces (login, restablecer contraseña) a partir de ella. En producción debe ser `https://...`.

### Criterios de salida
- [ ] La app no arranca sin `JWT_SECRET`.
- [ ] CORS configurable por entorno, sin barras finales ni comodines inválidos.
- [ ] `echo` desactivado por defecto.
- [ ] El backend rechaza contraseñas débiles (con test).
- [ ] Ningún enlace de correo está hardcodeado.
- [ ] `.env.example` actualizado con todas las variables nuevas.
- [ ] Tests nuevos para JWT, CORS básico y validación de contraseña.

---

## FASE 3 — Seguridad P1 (antes de producción)
## YOHAN MARTINEZ

### 3.1 Rate limiting global
- Hoy solo el login está limitado (5/min vía SlowAPI).
- Aplicar un **límite por defecto global** (SlowAPI `default_limits`, p. ej. `100/minute`) en lugar de decorar endpoint por endpoint, y límites más estrictos en endpoints sensibles: login, recuperación de contraseña, creación de usuarios, descarga de reportes.
- **Detalle técnico de SlowAPI:** los endpoints decorados con `@limiter.limit(...)` deben recibir `request: Request` como parámetro.
- Si hay proxy inverso (nginx), configurar la clave de identificación del cliente para que use la IP real (`X-Forwarded-For` de un proxy de confianza), o todos los usuarios compartirán la misma IP.

### 3.2 Paginación segura
- Auditar todos los endpoints de listado: ninguno debe poder devolver filas ilimitadas.
- Crear una dependencia reutilizable `PaginationParams` (`skip >= 0`, `limit` entre 1 y 100, por defecto 20) y aplicarla a los listados. Si el frontend depende hoy de recibir todo, coordinar el cambio (o ajustar el frontend en la Fase 6) y avisar al desarrollador.

### 3.3 Protección de reportes (DoS)
- Archivo: `reports.py` (módulo `reports` tras la Fase 1).
- Aplicar rate limit específico (p. ej. `5/minute`), límite máximo de filas por reporte y filtros obligatorios de rango de fechas cuando corresponda.
- Un límite en bytes del archivo generado en memoria solo sirve si se comprueba **durante** la generación; es mejor limitar filas/rango de fechas de entrada. Evalúa generación en streaming si los reportes son grandes.

### 3.4 Validación de entrada
- Revisar schemas y modelos: strings sin `max_length`, campos libres (`description`, notas) sin límite, números sin rangos (`ge`, `le`), emails/teléfonos sin formato.
- Añadir `Field(max_length=...)` y validadores con Pydantic v2 (`field_validator`). Alinear los límites con los largos de columna en BD.
- Recordatorio: el riesgo de "inyección" en campos de texto se mitiga con consultas parametrizadas (ORM) y con **escape en la salida** (frontend/HTML de correos), no con filtros caseros.

### 3.5 Cifrado de datos sensibles (NIT y teléfonos)
- **Antes de implementar, pregunta al desarrollador** qué campos exactamente cifrar y si se necesita buscar/filtrar por ellos (el cifrado Fernet no permite búsquedas por igualdad, ya que cada cifrado es distinto).
- Si hay que buscar por el campo, usar además un **índice ciego** (HMAC determinista del valor normalizado, en una columna aparte).
- Implementar con `TypeDecorator` de SQLAlchemy y una `ENCRYPTION_KEY` en variables de entorno (sin valor por defecto; la app no arranca sin ella).
- **Migración de datos existentes:** crear una migración de Alembic (con paso de datos) que cifre los valores actuales; incluir plan de rollback y haber hecho respaldo antes. Prever la rotación de claves (`MultiFernet`).
- Ajustar el tamaño de columna: el texto cifrado es bastante más largo que el original.

### 3.6 HTTPS y despliegue
- Documentar y verificar la configuración de nginx con TLS (redirección HTTP→HTTPS, HSTS, cabeceras de seguridad básicas).
- Asegurar que MySQL **no** esté expuesto al exterior en producción (el puerto 3307 mapeado en el diagrama debe existir solo en desarrollo).
- Respaldo automático de la BD: script programado (`mysqldump` o equivalente), retención definida y **prueba de restauración** documentada.

### Criterios de salida
- [ ] Rate limit global activo y probado.
- [ ] Ningún listado sin límite.
- [ ] Reportes con límites.
- [ ] Schemas con validaciones de longitud/rango.
- [ ] Datos sensibles cifrados con migración probada y respaldo previo.
- [ ] Compose de producción sin puertos de BD expuestos; backup documentado y restaurado con éxito al menos una vez.

---

## FASE 4 — Reglas de negocio y trazabilidad
## ISABEL MARTINEZ

### 4.1 Audit log
- Crear el modelo `AuditLog` (módulo `audit/`) con: `id`, `user_id`, `action`, `resource_type`, `resource_id`, `old_value` (JSON), `new_value` (JSON), `ip_address` (opcional), `timestamp` (UTC).
- Crear `AuditService.log_action(...)` y llamarlo **desde los servicios** (no desde los routers) en acciones críticas: crear/editar/eliminar usuarios, cambios de rol/permisos, cambio y reset de contraseña, anulación de ventas, ajustes de inventario, descarga de reportes, intentos de login fallidos relevantes.
- **Nunca** guardar contraseñas, hashes ni tokens en `old_value`/`new_value`; filtrar campos sensibles.
- El log debe ser **append-only**: sin endpoints de edición/borrado; lectura solo para admin.
- Migración de Alembic para la nueva tabla.

### 4.2 Máquina de estados para ventas
- **Confirma primero con el desarrollador** las reglas de negocio reales. Propuesta de partida de la auditoría:
  - Estados actuales: `COMPLETED`, `ANNULLED`.
  - Transición válida: `COMPLETED → ANNULLED`, solo dentro de las 24 h posteriores a la venta.
  - Al anular: restaurar el stock de cada ítem y registrar el movimiento de inventario, **todo en una sola transacción** (si algo falla, nada se aplica).
- Corrección a la propuesta original: no usar `(now - sale_date).days > 1` (compara días enteros y deja pasar hasta ~48 h). Usar `timedelta`:
  ```python
  if datetime.now(timezone.utc) - sale.sale_date > timedelta(hours=24):
      raise BusinessRuleError("Solo se pueden anular ventas dentro de 24 horas")
  ```
  Verificar el manejo de zonas horarias en `sale_date` (naive vs aware) para no comparar tipos incompatibles.
- Definir las transiciones permitidas en un único lugar (diccionario `ALLOWED_TRANSITIONS`) dentro del servicio.
- Proteger contra doble anulación concurrente (bloqueo de fila con `with_for_update()` al leer la venta).
- Registrar la anulación en el audit log (quién, cuándo, motivo).

### Criterios de salida
- [ ] Acciones críticas generan registros en `audit_log` (con tests).
- [ ] Ninguna información sensible aparece en el audit log.
- [ ] Anular una venta fuera de regla devuelve error de negocio claro; anular restaura stock de forma atómica.
- [ ] Tests de transiciones válidas e inválidas y de concurrencia básica.

---

## FASE 5 — Testing completo
## ISABEL MARTINEZ

Estructura objetivo:

```
backend/tests/
├── conftest.py
├── unit/            # servicios y utilidades puras (security, validators, state machine)
├── integration/     # endpoints con BD de test: auth, users, roles, sales, inventory, reports
└── e2e/             # flujos completos (login → venta → anulación → reporte)
```

### Prioridades de cobertura
1. **Seguridad:** login (éxito, fallo, rate limit), expiración de tokens, tokens manipulados, `require_module`/`require_admin` (acceso permitido/denegado por rol), recuperación de contraseña (token válido, expirado, reutilizado).
2. **Negocio crítico:** ventas (stock insuficiente, anulación, atomicidad), inventario.
3. **Validaciones:** contraseña, longitudes, paginación.
4. **Regresión de lo corregido en fases 2–4:** un test por cada hallazgo corregido.

### Criterios de salida
- [ ] Cobertura mínima acordada (sugerido ≥ 70 % en servicios y seguridad).
- [ ] Tests ejecutándose en CI (GitHub Actions u otro) en cada PR.
- [ ] Linter y type-check (`ruff`, `mypy` opcional) integrados al pipeline.

---

## FASE 6 — Frontend, logging y documentación
## NICOLE VEGA y test finales, paso 7, 8 y 9

### 6.1 Logging estructurado
- Reemplazar `logging.basicConfig(level=WARNING)` por configuración central (`core/logging.py`): formato JSON o estructurado, nivel por entorno, ID de petición (middleware) para correlacionar logs.
- No registrar datos sensibles (contraseñas, tokens, datos personales).
- Dejar preparado el envío a una plataforma centralizada (ELK/Datadog/Loki) como documento de diseño; implementarlo solo si el desarrollador lo pide.

### 6.2 Frontend
- Adoptar **TanStack Query** para datos del servidor (caché, reintentos, estados de carga/error) y dejar Context solo para estado de UI/sesión. Migrar pantalla por pantalla, empezando por listados.
- Adaptar el frontend a la paginación del backend (Fase 3.2).
- Verificar que el frontend envíe el header `session-token` y maneje 401/403/429 de forma consistente (cierre de sesión, mensaje de "demasiados intentos").
- Escapar/sanitizar cualquier contenido de usuario renderizado como HTML (evitar `dangerouslySetInnerHTML` con datos sin sanear).

### 6.3 Documentación de la API
- Completar `summary`, `description`, `responses` y ejemplos en los endpoints principales (códigos 400/401/403/404/409/422/429).
- Documentar reglas de negocio en el docstring de cada endpoint relevante (ej. ventas: stock, anulación en 24 h).
- Versionar el OpenAPI (prefijo `/api/v1` si el desarrollador lo aprueba; es un cambio de rutas, así que **pregunta antes**).

### 6.4 Documentación del proyecto
- `README.md`: cómo levantar dev y prod, variables de entorno obligatorias/opcionales.
- `docs/ARQUITECTURA.md`, `docs/SEGURIDAD.md` (política de contraseñas, rotación de secretos, respaldo/restauración), `docs/CONTRIBUIR.md` (convenciones de módulos y servicios).

---

## 7. Checklist final antes de producción

- [ ] `JWT_SECRET`, `ENCRYPTION_KEY`, credenciales SMTP y de BD definidos solo por entorno/gestor de secretos.
- [ ] CORS restringido a dominios reales, con HTTPS.
- [ ] `SQLALCHEMY_ECHO=false`, logs sin datos sensibles.
- [ ] Rate limiting global activo; paginación en todos los listados.
- [ ] Datos sensibles cifrados; backups automáticos y restauración probada.
- [ ] Audit log funcionando; ventas con máquina de estados.
- [ ] Suite de tests en CI en verde.
- [ ] MySQL no expuesto públicamente; contenedores sin root; healthchecks OK.
- [ ] Documentación actualizada.

---

## 8. Plazos orientativos

| Fase | Esfuerzo estimado |
|------|-------------------|
| 0 | 2–3 días |
| 1 | 1–1.5 sprints |
| 2 | 2–3 días |
| 3 | 1 sprint |
| 4 | 1 sprint |
| 5 | Continuo; cierre en 1 sprint |
| 6 | 1 sprint |

La auditoría original estimaba **2–3 sprints** hasta producción aplicando P0 y P1; con la Fase 1 de arquitectura al inicio, conviene planificar un poco más.

---

## 9. Notas de verificación sobre la auditoría original

Para que no apliques correcciones basadas en afirmaciones imprecisas:

1. **"SQL Injection" (echo=True):** el hallazgo real es **fuga de información en logs**, no inyección SQL. Aun así, verifica que no haya SQL por concatenación (ver 2.3).
2. **CORS y CSRF:** el token viaja en header (`session-token`), no en cookie, lo que reduce mucho el riesgo de CSRF clásico. El problema real de CORS es la configuración incorrecta (barra final, comodín inválido, orígenes innecesarios), no un CSRF directo.
3. **Matriz de riesgo:** las cantidades y clasificaciones de la sección "Matriz de riesgo" del informe no coinciden del todo con el detalle (por ejemplo, paginación y validación aparecen con distinta severidad). Guíate por este plan, no por la matriz.
4. **Rate limit con SlowAPI:** el ejemplo del informe omite el parámetro `request: Request`, necesario para que funcione.
5. **Límite de tamaño en reportes:** el ejemplo `MAX_REPORT_SIZE` del informe no se aplica por sí solo; hay que limitar filas/rango o verificar durante la generación.
6. **Cifrado Fernet:** el ejemplo del informe solo cubre el cifrado; falta el descifrado (`process_result_value`) y no contempla búsquedas ni migración de datos existentes (ver 3.5).
7. **Anulación de ventas:** el ejemplo usa `.days > 1`, que no equivale a 24 h (ver 4.2).
8. **Contexto del proyecto:** el informe se basa en una lectura puntual del código; si algo ya está resuelto o es distinto en el repositorio actual, **repórtalo y omite el paso**.
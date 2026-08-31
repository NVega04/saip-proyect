# Evidencia de Testing con Postman - SAIP (Punto 3.4)

**Fecha de ejecución:** 2026-08-27
**Entorno:** Backend real en `http://localhost:8000` (docker) · Base de datos `db_saip_proyect`
**Autenticación:** `POST /session/login` (`admin@saip.com` / `admin123`) → devuelve JWT en header `session-token`.

> **Herramienta:** Postman (GUI). La colección `SAIP_Pruebas_BD_vs_App.postman_collection.json` incluye todas las peticiones ya configuradas. Las capturas de pantalla de prueba (una por caso) se toman desde la GUI de Postman siguiendo esta guía; abajo se documenta el **request + response reales** de cada caso junto con la **verificación en BD** (esencia del punto 3.4: BD vs Aplicación).

---

## Resultado global

| Indicador | Valor |
|---|---|
| Endpoints probados | 5 |
| Casos por endpoint | 2 (positivo + negativo) |
| Casos totales | 10 |
| Casos pasados | 10 ✅ |
| Datos residuales en DB tras limpieza | 0 |
| Stock producto 3 (estado final) | 200 (íntegro) |

| Endpoint | Método | Positivo (HTTP) | Negativo (HTTP) |
|---|---|---|---|
| /users/ | POST | ✅ 201 | ✅ 404 |
| /roles/ | POST | ✅ 201 | ✅ 409 |
| /providers/ | POST | ✅ 201 | ✅ 409 |
| /units/ | POST | ✅ 201 | ✅ 422 |
| /sales/ + /sales/{id}/annul | POST/PATCH | ✅ 201 / ✅ 200 | ✅ 400 |

---

## 1. Login (obtener token)

**Request:** `POST http://localhost:8000/session/login`
```json
{ "email": "admin@saip.com", "password": "admin123", "accepted_terms": true }
```
**Response (HTTP 200):** devuelve `session_token` (JWT), `expires_at`, `user`. Tomar este token y colocarlo en el header `session-token` de las peticiones que lo requieran.

---

## 2. USERS - `POST /users/`

**Caso POSITIVO (201):**
```json
{ "first_name": "QA", "last_name": "TEST", "email": "qa.user.postman@saip.com", "role_id": 1, "is_admin": false }
```
→ `201` · usuario id=42, rol "Admin".
**Verificación DB:** fila persistió con `role_id=1`.
```sql
SELECT id,email,role_id,status FROM users WHERE email='qa.user.postman@saip.com';  -- 1 fila
```

**Caso NEGATIVO (404):** `role_id: 9999` (inexistente)
→ `404` `{"detail":"El rol con id '9999' no existe."}`
**Verificación DB:** 0 filas (no persistió).
```sql
SELECT COUNT(*) FROM users WHERE email='qa.user.neg@saip.com';  -- 0
```

---

## 3. ROLES - `POST /roles/`

**Caso POSITIVO (201):**
```json
{ "name": "QA POSTMAN", "description": "ROL CREADO DESDE POSTMAN" }
```
→ `201` · rol id=35.
**Verificación DB:** fila persistió.

**Caso NEGATIVO (409):** `name: "Admin"` (ya existe, la app normaliza a mayúsculas)
→ `409` `{"detail":"El rol 'ADMIN' ya existe."}`
**Verificación DB:** sigue existiendo un solo rol "Admin".

---

## 4. PROVIDERS - `POST /providers/`

**Caso POSITIVO (201):**
```json
{ "company": "PROVEEDOR POSTMAN QA", "nit": "777777777-7", "email": "prov.postman@saip.com" }
```
→ `201` · proveedor id=29 (requiere header `session-token`).
**Verificación DB:** fila persistió con `nit` único.

**Caso NEGATIVO (409):** `nit: "800123456-1"` (ya existe)
→ `409` `{"detail":"Ya existe un proveedor con el NIT '800123456-1'."}`
**Verificación DB:** sin duplicado de `nit`.

---

## 5. UNITS - `POST /units/`

**Caso POSITIVO (201):**
```json
{ "name": "QUINTAL POSTMAN", "abbreviation": "qq", "description": "UNIDAD QA", "quantity": 100 }
```
→ `201` · unidad id=26 (abreviatura normalizada a mayúsculas `QQ`).
**Verificación DB:** fila persistió.

**Caso NEGATIVO (422):** sin campo obligatorio `abbreviation`
```json
{ "name": "SIN ABREV QA", "quantity": 1 }
```
→ `422` `{"detail":[{"type":"missing","loc":["body","abbreviation"],...}]}`
**Verificación DB:** no se creó ninguna unidad.

---

## 6. SALES - `POST /sales/` y `PATCH /sales/{id}/annul` (caso transaccional)

**Producto de prueba:** id=3 "CROISSANT MANTEQUILLA", stock inicial **200**.

**Caso POSITIVO - Venta (201):**
```json
{ "items": [ { "item_type": "product", "item_id": 3, "quantity": 5 } ], "notes": "VENTA POSTMAN QA" }
```
→ `201` · venta id=6.
**Verificación DB — consistencia del stock (criterio transaccional):**
```sql
SELECT available_quantity FROM products WHERE id=3;  -- 200  (antes)
-- tras la venta: 195
SELECT movement_type,stock_before,stock_after FROM inventory_movements WHERE reference_id=6;
-- SALE | 200 | 195
```

**Caso POSITIVO - Anulación (200):**
`PATCH /sales/6/annul`
→ `200` `{"message":"Venta anulada y stock restaurado.",...}`
**Verificación DB — stock restaurado:**
```sql
SELECT available_quantity FROM products WHERE id=3;  -- 195  -> (tras anulación) 200
SELECT movement_type,stock_before,stock_after FROM inventory_movements WHERE reference_id=6;
-- SALE | 200 | 195
-- SALE_ANNULMENT | 195 | 200
```

**Caso NEGATIVO - Stock insuficiente (400):**
```json
{ "items": [ { "item_type": "product", "item_id": 3, "quantity": 100000 } ], "notes": "VENTA IMPOSIBLE" }
```
→ `400` `{"detail":"Stock insuficiente para 'CROISSANT MANTEQUILLA': disponible 200.0, solicitado 100000.0."}`
**Verificación DB — ROLLBACK correcto:**
```sql
SELECT available_quantity FROM products WHERE id=3;  -- 200 (sin cambio)
SELECT COUNT(*) FROM sales WHERE notes='VENTA IMPOSIBLE';  -- 0 (no persistió)
```
> Este caso demuestra el **criterio de reversión de datos (ROLLBACK)** exigido por el Punto 3.4 frente a una violación de regla de negocio/integridad.

---

## Cómo tomar las capturas de pantalla en Postman (paso a paso)

1. Importa la colección: **Import** → selecciona `SAIP_Pruebas_BD_vs_App.postman_collection.json`.
2. Abre la petición **"0. Login"**, presiona **Send** y copia el `session_token` a la variable de colección (`session_token`) o a cada header de petición.
3. Ejecuta cada petición y, en la pestaña **Response**, captura la pantalla mostrando:
   - el **método + URL** (título de la petición),
   - el **código de estado** (ej. `201 Created`),
   - el **body de respuesta**.
4. Guarda cada captura como `postman_<endpoint>_<pos|neg>.png` (ej. `postman_users_pos.png`).

Sugerencia de nombres de capturas:
`postman_login.png`, `postman_users_pos.png`, `postman_users_neg.png`, `postman_roles_pos.png`, `postman_roles_neg.png`, `postman_providers_pos.png`, `postman_providers_neg.png`, `postman_units_pos.png`, `postman_units_neg.png`, `postman_sales_pos.png`, `postman_sales_annul.png`, `postman_sales_neg.png`.

---

## Limpieza

Tras ejecutar las pruebas, se eliminaron todos los registros de prueba de la BD (usuario QA, rol QA, proveedor QA, unidad QA y la venta de prueba anulada con sus movimientos). La base quedó en su estado original: 1 venta real, stock del producto 3 = **200**.

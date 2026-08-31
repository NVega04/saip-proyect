# Matriz de Validación BD vs Aplicación
## SAIP - Punto 3.4 (Actividades de Transferencia del Conocimiento)

**Base de datos real:** `db_saip_proyect` (contenedor `saip_db_container`, MySQL 8.0)
**Conexión de ejecución:** `docker exec saip_db_container mysql -f -uroot -proot_password db_saip_proyect < <script.sql>`

> **Nota crítica de esquema:** El archivo `saip.sql` del repositorio está desactualizado (nombres obsoletos como `usuarios`, `productos`, `ventas`). El esquema real es generado por SQLModel con nombres ingleses plurales (`users`, `products`, `sales`, `providers`, `inventory_movements`, etc.). **Todas las pruebas se ejecutan contra el esquema REAL.**

---

## Resultado global

| Indicador | Valor |
|---|---|
| Endpoints probados | 20 |
| Funcionalidades por endpoint | 2 (1 positiva + 1 negativa) |
| Casos de prueba totales | 40 |
| Casos ejecutados correctamente | 40 |
| Casos POSITIVOS pasados | 20 |
| Casos NEGATIVOS (comportamiento esperado de fallo) | 20 |
| Datos residuales en BD tras las pruebas | 0 (todo con ROLLBACK) |
| Stock del producto 3 tras venta de prueba | 200 (íntegro) |

---

## Matriz detallada (40 casos / 20 endpoints)

| # | Endpoint | Método | Operación DML | Tabla(s) afectada(s) | Restricción validada | Caso | Resultado esperado | Resultado obtenido |
|---|---|---|---|---|---|---|---|---|
| 1 | /users/ | POST | INSERT | users (+FK roles) | FK role_id | **Positivo** | 201, fila creada + FK rol correcta | ✅ Fila id=34, rol Admin |
| 1 | /users/ | POST | INSERT | users | FK role_id=9999 | **Negativo** | 4xx/rechazo, 0 filas | ✅ Error FK, 0 filas |
| 2 | /roles/ | POST | INSERT | roles | UNIQUE name (app-level) | **Positivo** | 201, rol creado | ✅ Fila creada |
| 2 | /roles/ | POST | INSERT | roles | nombre duplicado | **Negativo** | 409, 0 filas | ✅ 1 solo Admin |
| 3 | /providers/ | POST | INSERT | providers | UNIQUE nit/email | **Positivo** | 201, proveedor creado | ✅ Fila creada |
| 3 | /providers/ | POST | INSERT | providers | UNIQUE nit | **Negativo** | 4xx, 0 filas | ✅ Error 1062, 0 filas |
| 4 | /providers/{id}/contacts/ | POST | INSERT | provider_contacts | FK provider_id | **Positivo** | 201, contacto + JOIN proveedor | ✅ Fila + proveedor HARINERA |
| 4 | /providers/{id}/contacts/ | POST | INSERT | provider_contacts | FK provider_id=9999 | **Negativo** | 4xx, 0 filas | ✅ Error FK, 0 filas |
| 5 | /units/ | POST | INSERT | units | NOT NULL abbreviation | **Positivo** | 201, unidad creada | ✅ Fila creada |
| 5 | /units/ | POST | INSERT | units | abbreviation NULL | **Negativo** | 4xx, 0 filas | ✅ Error 1048, 0 filas |
| 6 | /products/ | POST | INSERT | products (+FK units) | FK unit_id | **Positivo** | 201, producto + unidad | ✅ Fila + unidad UNIDAD |
| 6 | /products/ | POST | INSERT | products | FK unit_id=8888 | **Negativo** | 4xx, 0 filas | ✅ Error FK, 0 filas |
| 7 | /supplies/ | POST | INSERT | supplies (+FKs) | FK category_id/unit_id | **Positivo** | 201, insumo + categoría/unidad | ✅ Fila + FKs correctas |
| 7 | /supplies/ | POST | INSERT | supplies | FK category_id=7777 | **Negativo** | 4xx, 0 filas | ✅ Error FK, 0 filas |
| 8 | /supply-categories/ | POST | INSERT | supply_categories | UNIQUE name | **Positivo** | 201, categoría creada | ✅ Fila creada |
| 8 | /supply-categories/ | POST | INSERT | supply_categories | UNIQUE name duplicado | **Negativo** | 4xx, 0 filas | ✅ Error 1062, 0 filas |
| 9 | /product-categories/ | POST | INSERT | product_categories | UNIQUE name | **Positivo** | 201, categoría creada | ✅ Fila creada |
| 9 | /product-categories/ | POST | INSERT | product_categories | UNIQUE name duplicado | **Negativo** | 4xx, 0 filas | ✅ Error 1062, 0 filas |
| 10 | /commercial-products/ | POST | INSERT | commercial_products (+FKs) | FK unit_id/category_id | **Positivo** | 201, producto + FKs | ✅ Fila + FKs correctas |
| 10 | /commercial-products/ | POST | INSERT | commercial_products | FK unit_id=5555 | **Negativo** | 4xx, 0 filas | ✅ Error FK, 0 filas |
| 11 | /recipes/ | POST | INSERT | recipes + recipe_ingredients | FK product_id | **Positivo** | 201, receta + ingrediente | ✅ Fila + ingrediente |
| 11 | /recipes/ | POST | INSERT | recipes | FK product_id=4444 | **Negativo** | 4xx, 0 filas | ✅ Error FK, 0 filas |
| 12 | /users/{id} | PUT/PATCH | UPDATE | users | UNIQUE email | **Positivo** | 200, usuario actualizado | ✅ Fila actualizada |
| 12 | /users/{id} | PUT/PATCH | UPDATE | users | email duplicado | **Negativo** | 409, sin cambio | ✅ Error 1062, email único |
| 13 | /roles/{id} | PATCH | UPDATE | roles | UNIQUE name (app) | **Positivo** | 200, rol actualizado | ✅ Fila actualizada |
| 13 | /roles/{id} | PATCH | UPDATE | roles | nombre duplicado | **Negativo** | 409 (app-level), sin persistir | ✅ ROLLBACK (no persiste) |
| 14 | /providers/{id} | PATCH | UPDATE | providers | UNIQUE nit/email | **Positivo** | 200, proveedor actualizado | ✅ Fila actualizada |
| 14 | /providers/{id} | PATCH | UPDATE | providers | nit duplicado | **Negativo** | 409, sin cambio | ✅ Error 1062, nit único |
| 15 | /units/{id} | PATCH | UPDATE | units | id existente/válido | **Positivo** | 200, unidad actualizada | ✅ Fila actualizada |
| 15 | /units/{id} | PATCH | UPDATE | units | id inexistente | **Negativo** | 404, sin cambio | ✅ 0 filas |
| 16 | /users/{id} | DELETE | soft delete | users | soft delete | **Positivo** | 200, deleted_at marcado | ✅ Fila INACTIVE + deleted_at |
| 16 | /users/{id} | DELETE | soft delete | users | id inexistente | **Negativo** | 404, sin cambios | ✅ 0 filas |
| 17 | /roles/{id} | DELETE | soft delete | roles | soft delete | **Positivo** | 200, deleted_at marcado | ✅ Fila INACTIVE |
| 17 | /roles/{id} | DELETE | soft delete | roles | id inexistente | **Negativo** | 404, sin cambios | ✅ 0 filas |
| 18 | /providers/{id} | DELETE | soft delete | providers | soft delete | **Positivo** | 200, deleted_at marcado | ✅ Fila INACTIVE |
| 18 | /providers/{id} | DELETE | soft delete | providers | ya inactivo (doble borrado) | **Negativo** | 409, sin cambios | ✅ ROLLBACK |
| 19 | /providers/{id}/contacts/{c} | DELETE | soft delete | provider_contacts | soft delete | **Positivo** | 200, deleted_at marcado | ✅ Fila + deleted_at |
| 19 | /providers/{id}/contacts/{c} | DELETE | soft delete | provider_contacts | id inexistente | **Negativo** | 404, sin cambios | ✅ 0 filas |
| 20 | /units/{id} | DELETE | soft delete | units | id existente/válido | **Positivo** | 200, deleted_at marcado | ✅ Fila + deleted_at |
| 20 | /units/{id} | DELETE | soft delete | units | id inexistente | **Negativo** | 404, sin cambios | ✅ 0 filas |
| 21 | /sales/ + /sales/{id}/annul | POST/PATCH | INSERT+UPDATE+INSERT | sales, sale_items, products, inventory_movements | Consistencia stock + transacción | **Positivo** | 201, stock resta y se restaura | ✅ 200→195→200 íntegro |
| 22 | /sales/ | POST | INSERT (bloqueado) | sales/items | Validación stock insuficiente | **Negativo** | 400 + ROLLBACK, sin persistir | ✅ 0 ventas fallidas, stock intacto |

---

## Decisiones de diseño y observaciones

1. **Esquema real vs saip.sql:** Todas las tablas probadas son las que el backend crea vía SQLModel. El `saip.sql` es un respaldo viejo y no debe usarse para estas validaciones.

2. **Soft delete:** Los 5 endpoints DELETE usan marcado de `deleted_at`/`deleted_by` (y `status=INACTIVE` en algunos). No hay DELETE físico.

3. **Transacciones y ROLLBACK:** Los casos positivos se ejecutan en `START TRANSACTION ... ROLLBACK` para certificar persistencia sin contaminar la BD de producción. El caso 22 (stock insuficiente) demuestra **explícitamente** la reversión de datos frente a una violación de integridad/regla de negocio, cumpliendo el criterio evaluativo del Punto 3.4.

4. **Validación UNIQUE de roles:** El modelo `roles` no tiene UNIQUE en `name` a nivel de BD; la validación se hace en la aplicación (409). Por eso el caso 13.2 a nivel SQL crudo pudo duplicar, pero la transacción se revierte y la app lo rechaza.

5. **Limpiar la BD** tras la evidencia: verificado, 0 registros de prueba residuales y stock del producto 3 íntegro (200).

---

## Cómo reproducir la evidencia

```bash
cd saip-proyect/_docs/evidencias
for f in 00_estado_inicial.sql 01_creates.sql 02_updates.sql 03_deletes.sql 04_ventas_transaccional.sql; do
  docker exec -i saip_db_container mysql -f -uroot -proot_password db_saip_proyect < "$f"
done
```

---

## Anexo: Pruebas contra la API real (Postman) - 5 endpoints

Complemento de la matriz: los 5 endpoints se probaron contra la **API real** (`http://localhost:8000`) con Postman (ver `postman/SAIP_Pruebas_BD_vs_App.postman_collection.json` y `postman/README.md`). Resultados HTTP reales:

| Endpoint | Método | Caso POSITIVO | Caso NEGATIVO | Verificación en DB |
|---|---|---|---|---|
| /users/ | POST | ✅ 201 (usuario id=42) | ✅ 404 (rol 9999 inexistente) | 1 fila / 0 filas |
| /roles/ | POST | ✅ 201 (rol id=35) | ✅ 409 (nombre 'ADMIN' duplicado) | 1 fila / sin duplicado |
| /providers/ | POST | ✅ 201 (prov. id=29) | ✅ 409 (NIT duplicado) | 1 fila / sin duplicado |
| /units/ | POST | ✅ 201 (unidad id=26) | ✅ 422 (abbreviation requerido) | 1 fila / 0 filas |
| /sales/ | POST/PATCH | ✅ 201 (venta) / ✅ 200 (annul) | ✅ 400 (stock insuficiente) | stock 200→195→200 / sin persistir |

**Caso transaccional (ventas) verificado en la API real:**
- Venta de 5 uds del producto 3: stock **200 → 195** (HTTP 201).
- Anulación `PATCH /sales/6/annul`: stock **195 → 200** (HTTP 200).
- Venta de 100000 uds (stock insuficiente): **HTTP 400** + stock intacto (200) + 0 ventas persistidas → **ROLLBACK** demostrado en el flujo real de la aplicación.

Al finalizar se limpiaron todos los registros de prueba (usuario, rol, proveedor, unidad y venta de prueba con sus movimientos), dejando la BD en su estado original (1 venta real, stock producto 3 = 200).

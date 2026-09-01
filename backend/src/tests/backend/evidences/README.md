# Evidencias - Punto 3.4 Automatización de API con Postman

Carpeta de evidencias de la suite automatizada **SAIP API Tests** para el
proyecto formativo SAIP (punto 3.4 de la guía GFPI-F-135).

## Documentos fuente

- Colección: `../postman/SAIP_API_Tests.postman_collection.json`
- Environment: `../postman/SAIP_Local.postman_environment.json`

## Cómo ejecutar la suite

1. Levantar el backend (levanta también la base de datos):
   ```bash
   docker-compose up --build backend
   ```
2. Verificar que responde:
   ```bash
   curl http://localhost:8000/docs
   ```
3. En Postman importar (File) los dos archivos JSON de la carpeta `postman/`.
   - Si Postman pregunta por reemplazo, responder **Reemplazar**.
4. Seleccionar el environment **SAIP Local** (arriba a la derecha).
5. Sobre la colección **SAIP API Tests** → **···** → **Run collection** → **Run SAIP API Tests**.
6. El Login tiene límite de 5 intentos por minuto (`/session/login`): ejecutar la
   suite una sola vez por minuto para evitar un error 429.

## Resultado esperado

- **26 requests** ejecutadas en orden (Auth → Users → Units → SupplyCategories →
  Products → Supplies → Cleanup), encadenando variables dinámicas (token e IDs).
- **0 failed / 0 errors** en el Collection Runner.

## Evidencias registradas

| Archivo | Descripción |
|---|---|
| `SAIP API Tests.postman_test_run.json` | Exportación del resultado de la ejecución del Collection Runner. |
| `Runner_resumen_0failures.png` | Captura del resumen general del Runner (0 failures). |
| `Runner_crear_producto_201.png` | Captura de una petición individual (Crear producto - 201). |

> Las capturas de pantalla las genera Postman de forma nativa; aquí se guardan
> para documentar la ejecución de la suite.

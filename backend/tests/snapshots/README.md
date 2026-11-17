# Snapshot OpenAPI — procedencia y política

`openapi_baseline.json` es el contrato OpenAPI de SAIP **antes** del refactor de
la Fase 1. Es la referencia contra la que `tests/test_openapi_snapshot.py`
verifica que la API no cambió de forma accidental.

## Procedencia

| Dato | Valor |
|---|---|
| Commit de origen | `0f86777` (`master`, previo a `fase-1-arquitectura`) |
| Generado con | `app.openapi()` de la aplicación en ese commit |
| Paths | 59 |
| Schemas | 120 |
| SHA-256 | `3f2bc1bef68fca4138e88d4abd996c7fafbd02958e1f08f948a6eeb3f1295902` |

Se verificó en tres vías que el OpenAPI del commit `0f86777`, el de este
snapshot y el de la rama `fase-1-arquitectura` son idénticos.

## Política

1. **Nunca** se regenera el snapshot para que un test pase.
2. Un cambio de contrato (ruta, método, schema, código de respuesta) debe ser
   intencional y aprobado por el equipo. En ese caso:
   - se actualiza `openapi_baseline.json`;
   - se actualiza la tabla de arriba (conteos y SHA-256);
   - se explica el motivo en el mensaje del commit.
3. Las diferencias de `servers` se ignoran por ser volátiles.
4. Los cambios de comportamiento que no alteran el contrato (lógica interna,
   contenido de un Excel, envío de correos) **no** los detecta este test; para
   eso están los tests de humo y, más adelante, los tests de integración.

## Cómo verificar

```bash
docker compose run --rm backend uv run pytest tests/test_openapi_snapshot.py -q
```

Resultado esperado: `2 passed` (comparación + forma del baseline).

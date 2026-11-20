# Snapshot OpenAPI — procedencia y política

`openapi_baseline.json` es el contrato OpenAPI aprobado de SAIP. Es la
referencia contra la que `tests/test_openapi_snapshot.py` verifica que la API
no cambie de forma accidental.

## Procedencia

| Dato | Valor |
|---|---|
| Commit de origen | `0f86777` (`master`, previo a `fase-1-arquitectura`) |
| Actualizado en | `fase-4-reglas-trazabilidad` (cambio aprobado) |
| Generado con | `app.openapi()` de la aplicación actual |
| Paths | 60 |
| Schemas | 123 |
| SHA-256 | `d5b5f24dcf9683f3a1b5d74bac9a4659cba801f519233407fbf06ced6350607a` |

## Cambio aprobado en Fase 4

- Se agregó `GET /audit/` con los schemas `AuditLogResponse` y `AuditLogPage`.
- Se agregó `SaleAnnulRequest.reason` al contrato de anulación de ventas.
- El owner del endpoint de anulación pasó a ser el módulo RBAC `sales`.

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
   eso están los tests de humo y los tests de integración.

## Cómo verificar

```bash
docker compose run --rm backend uv run pytest tests/test_openapi_snapshot.py -q
```

Resultado esperado: `2 passed` (comparación + forma del baseline).

"""El contrato OpenAPI no debe cambiar sin una decisión explícita.

Convierte en test la comparación que antes vivía en
``tests/check_openapi_snapshot.py``. El baseline se generó originalmente desde
``master`` (``0f86777``) y se actualizó en la Fase 4 para reflejar, con
aprobación explícita, el endpoint de auditoría y el motivo de anulación.
"""

import json
from pathlib import Path
from typing import Any

from src.main import app

SNAPSHOT = Path(__file__).parent / "snapshots" / "openapi_baseline.json"

# ``servers`` es volátil (depende del host que sirve la documentación) y
# ``paths`` se compara por separado para producir mensajes más claros.
IGNORED_TOP_LEVEL_KEYS = {"paths", "servers"}


def _load_baseline() -> dict[str, Any]:
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def _diff(left: Any, right: Any, path: str = "") -> list[tuple[str, Any, Any]]:
    differences: list[tuple[str, Any, Any]] = []

    if type(left) is not type(right):
        return [(path, left, right)]

    if isinstance(left, dict):
        for key in sorted(set(left) | set(right)):
            if key not in left:
                differences.append((f"{path}/{key}", "<ausente>", right[key]))
            elif key not in right:
                differences.append((f"{path}/{key}", left[key], "<ausente>"))
            else:
                differences += _diff(left[key], right[key], f"{path}/{key}")
    elif isinstance(left, list):
        if len(left) != len(right):
            differences.append((f"{path}/len", len(left), len(right)))
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            differences += _diff(left_item, right_item, f"{path}[{index}]")
    elif left != right:
        differences.append((path, left, right))

    return differences


def _openapi_differences(
    baseline: dict[str, Any], current: dict[str, Any]
) -> list[tuple[str, Any, Any]]:
    differences: list[tuple[str, Any, Any]] = []

    for key in sorted(set(baseline) | set(current)):
        if key in IGNORED_TOP_LEVEL_KEYS:
            continue
        differences += _diff(baseline.get(key), current.get(key), key)

    baseline_paths = set(baseline.get("paths", {}))
    current_paths = set(current.get("paths", {}))

    for path in sorted(baseline_paths - current_paths):
        differences.append((path, "presente en baseline", "ausente"))
    for path in sorted(current_paths - baseline_paths):
        differences.append((path, "ausente en baseline", "presente"))

    for path in sorted(baseline_paths & current_paths):
        baseline_methods = baseline["paths"][path]
        current_methods = current["paths"][path]
        for method in sorted(set(baseline_methods) | set(current_methods)):
            label = f"{method.upper()} {path}"
            if method not in baseline_methods:
                differences.append((label, "ausente", "presente"))
            elif method not in current_methods:
                differences.append((label, "presente", "ausente"))
            else:
                differences += _diff(
                    baseline_methods[method], current_methods[method], label
                )

    return differences


def test_openapi_matches_the_approved_baseline():
    differences = _openapi_differences(_load_baseline(), app.openapi())

    formatted = "\n".join(
        json.dumps(item, ensure_ascii=False, default=str) for item in differences[:50]
    )
    assert not differences, (
        f"El OpenAPI cambió respecto al baseline ({len(differences)} diferencia(s)). "
        "Si el cambio es intencional, actualiza el snapshot con aprobación "
        "explícita y documenta el motivo en el commit:\n" + formatted
    )


def test_baseline_has_the_expected_shape():
    baseline = _load_baseline()

    assert len(baseline["paths"]) == 60
    assert len(baseline["components"]["schemas"]) == 123

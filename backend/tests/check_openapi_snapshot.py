"""Compara el OpenAPI actual contra el snapshot baseline de la Fase 0."""

import json
import sys
from pathlib import Path

from src.main import app

SNAPSHOT = Path(__file__).parent / "snapshots" / "openapi_baseline.json"


def diff(a, b, path=""):
    out = []
    if type(a) is not type(b):
        return [(path, a, b)]
    if isinstance(a, dict):
        for key in sorted(set(a) | set(b)):
            if key not in a:
                out.append((f"{path}/{key}", "<missing>", b[key]))
            elif key not in b:
                out.append((f"{path}/{key}", a[key], "<missing>"))
            else:
                out += diff(a[key], b[key], f"{path}/{key}")
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append((f"{path}/len", len(a), len(b)))
        for index, (left, right) in enumerate(zip(a, b)):
            out += diff(left, right, f"{path}[{index}]")
    elif a != b:
        out.append((path, a, b))
    return out


def main() -> int:
    baseline = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    current = app.openapi()

    differences = []
    for key in sorted(set(baseline) | set(current)):
        if key in {"paths", "servers"}:
            continue
        differences += diff(baseline.get(key), current.get(key), key)

    base_paths = set(baseline.get("paths", {}))
    current_paths = set(current.get("paths", {}))
    for path in sorted(base_paths - current_paths):
        differences.append((path, "presente en baseline", "ausente"))
    for path in sorted(current_paths - base_paths):
        differences.append((path, "ausente en baseline", "presente"))

    for path in sorted(base_paths & current_paths):
        base_methods = baseline["paths"][path]
        current_methods = current["paths"][path]
        for method in sorted(set(base_methods) | set(current_methods)):
            if method not in base_methods:
                differences.append((f"{method.upper()} {path}", "ausente", "presente"))
            elif method not in current_methods:
                differences.append((f"{method.upper()} {path}", "presente", "ausente"))
            else:
                differences += diff(
                    base_methods[method],
                    current_methods[method],
                    f"{method.upper()} {path}",
                )

    if differences:
        print(f"OpenAPI diferente del baseline: {len(differences)} diferencia(s)")
        for item in differences[:50]:
            print(json.dumps(item, ensure_ascii=False, default=str))
        return 1

    print(
        f"OpenAPI idéntico al baseline: {len(current_paths)} paths, "
        f"{len(current.get('components', {}).get('schemas', {}))} schemas"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

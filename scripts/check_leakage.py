"""Run static imagination dependency checks without importing optional simulators."""

from __future__ import annotations

import ast
from pathlib import Path


def check(root: Path) -> list[str]:
    violations: list[str] = []
    for path in (root / "morphdream" / "imagination").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            module = None
            if isinstance(node, ast.Import):
                module = node.names[0].name
            elif isinstance(node, ast.ImportFrom):
                module = node.module
            if module and (module.startswith("morphdream.sim") or module.startswith("mujoco")):
                violations.append(f"{path}: {module}")
    return violations


if __name__ == "__main__":
    errors = check(Path(__file__).resolve().parents[1])
    if errors:
        raise SystemExit("\n".join(errors))
    print("imagination dependency boundary OK")

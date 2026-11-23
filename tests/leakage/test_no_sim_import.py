"""Static dependency guard for the dream/imagination boundary."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGINATION = ROOT / "morphdream" / "imagination"


def _imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def test_imagination_does_not_import_simulator() -> None:
    violations: list[str] = []
    for path in sorted(IMAGINATION.rglob("*.py")):
        for module in _imported_modules(path):
            if module == "morphdream.sim" or module.startswith("morphdream.sim."):
                violations.append(f"{path.relative_to(ROOT)} imports {module}")
    message = (
        "imagination may only consume snapshots, not simulator state: " + "; ".join(violations)
    )
    assert not violations, message


def test_imagination_has_no_direct_mujoco_dependency() -> None:
    violations: list[str] = []
    for path in sorted(IMAGINATION.rglob("*.py")):
        for module in _imported_modules(path):
            if module in {"mujoco", "mujoco_warp"} or module.startswith(("mujoco.", "mujoco_warp.")):
                violations.append(f"{path.relative_to(ROOT)} imports {module}")
    assert not violations, "imagination must remain backend independent: " + "; ".join(violations)

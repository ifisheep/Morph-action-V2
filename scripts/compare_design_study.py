"""Compare two design_study.json files with a numeric tolerance.

Physics results are deterministic on one machine, but the last digits of
floating-point results can differ across platforms (for example macOS arm64
against Linux x86_64). This script checks reproducibility the way it matters:

* floats must agree within ``--atol`` (default 1e-3);
* booleans, integers, strings, ``None`` and list lengths must match exactly,
  so a flipped "posture reached", a changed coverage fraction or a different
  worst joint is always reported;
* keys listed with ``--ignore`` (default: ``render``) are skipped.

Exit status 0 means no difference beyond tolerance.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

DEFAULT_ATOL = 1e-3


def compare(a: Any, b: Any, *, atol: float = DEFAULT_ATOL, ignore: frozenset[str] = frozenset({"render"}), path: str = "$") -> tuple[list[str], int, float]:
    """Return (differences, number of compared leaves, largest float difference)."""
    if isinstance(a, dict) and isinstance(b, dict):
        diffs: list[str] = []
        count, worst = 0, 0.0
        for key in sorted(set(a) | set(b)):
            if key in ignore:
                continue
            if key not in a or key not in b:
                diffs.append(f"{path}.{key}: present in only one file")
                continue
            d, c, w = compare(a[key], b[key], atol=atol, ignore=ignore, path=f"{path}.{key}")
            diffs += d
            count += c
            worst = max(worst, w)
        return diffs, count, worst
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: list length {len(a)} != {len(b)}"], 1, 0.0
        diffs, count, worst = [], 0, 0.0
        for index, (x, y) in enumerate(zip(a, b)):
            d, c, w = compare(x, y, atol=atol, ignore=ignore, path=f"{path}[{index}]")
            diffs += d
            count += c
            worst = max(worst, w)
        return diffs, count, worst
    if isinstance(a, float) or isinstance(b, float):
        if isinstance(a, bool) or isinstance(b, bool) or not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            return [f"{path}: {a!r} != {b!r}"], 1, 0.0
        delta = abs(float(a) - float(b))
        if math.isnan(delta) or delta > atol:
            return [f"{path}: {a!r} != {b!r} (|diff| {delta:.3g} > {atol:g})"], 1, delta
        return [], 1, delta
    if a != b or type(a) is not type(b):
        return [f"{path}: {a!r} != {b!r}"], 1, 0.0
    return [], 1, 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--atol", type=float, default=DEFAULT_ATOL)
    parser.add_argument("--ignore", nargs="*", default=["render"])
    parser.add_argument("--show", type=int, default=20, help="number of differences to print")
    args = parser.parse_args()
    a = json.loads(args.reference.read_text(encoding="utf-8"))
    b = json.loads(args.candidate.read_text(encoding="utf-8"))
    diffs, count, worst = compare(a, b, atol=args.atol, ignore=frozenset(args.ignore))
    print(f"compared {count} values; largest float difference {worst:.3g}; tolerance {args.atol:g}")
    if diffs:
        print(f"{len(diffs)} difference(s) beyond tolerance:")
        for line in diffs[: args.show]:
            print(f"  {line}")
        raise SystemExit(1)
    print("no differences beyond tolerance")


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import os
from pathlib import Path


def load_manifest(path: str | Path) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    groups = [set(payload.get(key, [])) for key in ("development", "validation", "test")]
    if any(groups[i] & groups[j] for i in range(3) for j in range(i + 1, 3)):
        raise ValueError("split manifest contains overlapping scene ids")
    if payload.get("immutable") is not True:
        raise ValueError("split manifest must be marked immutable")
    return payload


def require_test_opt_in(split: str) -> None:
    if split == "test" and os.getenv("ALLOW_TEST") != "1":
        raise PermissionError("set ALLOW_TEST=1 for test-split evaluation")

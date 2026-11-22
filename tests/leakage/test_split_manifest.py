"""Basic integrity checks for committed split manifests."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPLITS = ROOT / "splits"


def test_split_manifests_have_disjoint_scene_ids() -> None:
    manifests = sorted(SPLITS.glob("*.json"))
    assert manifests, "at least one smoke split manifest is required"
    for path in manifests:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload.get("immutable") is True
        groups = [payload.get(name, []) for name in ("development", "validation", "test")]
        seen: set[str] = set()
        for group in groups:
            assert isinstance(group, list)
            assert all(isinstance(scene_id, str) and scene_id for scene_id in group)
            assert seen.isdisjoint(group), f"scene overlap in {path.name}"
            seen.update(group)


def test_split_documentation_requires_explicit_test_opt_in() -> None:
    readme = (SPLITS / "README.md").read_text(encoding="utf-8")
    assert "ALLOW_TEST=1" in readme

"""Tolerance-based reproducibility check for design_study.json (task R3)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("compare_design_study", ROOT / "scripts/compare_design_study.py")
compare_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(compare_module)
compare = compare_module.compare


def test_small_float_noise_and_negative_zero_pass() -> None:
    a = {"qpos": [0.0, 1.000001, -0.25], "torque": 1.2491}
    b = {"qpos": [-0.0, 1.000002, -0.2502], "torque": 1.2494}
    diffs, count, worst = compare(a, b)
    assert diffs == []
    assert count == 4
    assert worst < 1e-3


def test_discrete_changes_are_always_reported() -> None:
    reference = {"reached": True, "joint": "spine_0_pitch", "contacts": 4, "coverage": 0.60, "items": [1, 2]}
    for key, value in (("reached", False), ("joint", "neck_pitch"), ("contacts", 5), ("coverage", 0.65), ("items", [1])):
        diffs, _, _ = compare(reference, {**reference, key: value})
        assert len(diffs) == 1 and key in diffs[0]


def test_missing_keys_and_ignored_keys() -> None:
    diffs, _, _ = compare({"a": 1, "render": "x.png"}, {"a": 1, "render": None})
    assert diffs == []
    diffs, _, _ = compare({"a": 1, "b": 2}, {"a": 1})
    assert diffs == ["$.b: present in only one file"]

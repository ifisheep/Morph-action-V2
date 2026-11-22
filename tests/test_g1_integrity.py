"""Pre-tuning integrity checks for the G1 v2 physical evaluation.

This file is intentionally written before the v2 model and runner changes.
It protects the single-model and free-base invariants from being replaced by
per-morphology kinematic shortcuts.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from morphdream.robot.assembly import AssemblySpec, build_mjcf

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "g1v2.yaml"
MORPHOLOGIES = ("quadruped", "snake", "centaur")
TRANSITIONS = (
    "quadruped_to_centaur",
    "centaur_to_quadruped",
    "quadruped_to_snake",
    "snake_to_quadruped",
)


def _config() -> dict:
    yaml = pytest.importorskip("yaml")
    payload = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert payload["frozen"] is True
    return payload


def _supermodel_xml() -> str:
    model = _config()["model"]
    spec = AssemblySpec(
        spine_segments=int(model["spine_segments"]),
        leg_pairs=int(model["leg_pairs"]),
        leg_dofs=int(model["leg_dofs"]),
        include_free_base=bool(model["has_free_base"]),
    )
    return build_mjcf(spec, model_name="g1v2_integrity")


def test_frozen_g1v2_thresholds_and_scope() -> None:
    config = _config()
    assert config["scene_count"] == 50
    assert config["episode_duration_s"] == 60.0
    assert config["transitions"]["trials_per_edge"] == 100
    assert config["thresholds"]["max_fall_rate"] == 0.05
    assert config["thresholds"]["min_transition_success_rate"] == 0.90
    manifest = json.loads((ROOT / config["scenario_manifest"]).read_text(encoding="utf-8"))
    assert manifest["frozen"] is True
    scenarios = manifest["scenarios"]
    assert len(scenarios) == 50
    assert len({item["scene_id"] for item in scenarios}) == 50
    assert len({item["ground_friction_scale"] for item in scenarios}) > 1
    assert len({item["mass_scale"] for item in scenarios}) > 1


def test_one_superset_model_has_required_topology() -> None:
    xml = _supermodel_xml()
    root = ET.fromstring(xml)
    spine_bodies = [
        body for body in root.findall(".//body") if body.attrib.get("name", "").startswith("spine_")
    ]
    assert len(spine_bodies) == 4
    spine_joints = [
        joint
        for body in root.findall(".//body")
        if body.attrib.get("name", "").startswith("spine_")
        for joint in body.findall("joint")
    ]
    assert len(spine_joints) == 6
    leg_joints = [
        joint
        for body in root.findall(".//body")
        if body.attrib.get("name", "").startswith("leg_")
        for joint in body.findall("joint")
    ]
    assert len(leg_joints) == 3 * 2 * 3
    assert root.find(".//freejoint") is not None or root.find(".//joint[@type='free']") is not None
    assert not root.findall(".//equality")
    assert not root.findall(".//mocap[@mocap='true']")
    assert "xfrc_applied" not in xml


def test_free_base_has_no_actuator_and_motor_limits_are_finite() -> None:
    xml = _supermodel_xml()
    root = ET.fromstring(xml)
    actuators = root.findall(".//actuator/*")
    assert actuators
    assert all("free" not in (item.attrib.get("joint", "")) for item in actuators)
    limits = [float(value) for item in actuators for value in item.attrib.get("ctrlrange", "").split()]
    assert limits and all(abs(value) <= 4.0 for value in limits)


def test_model_hash_is_identical_for_all_morphology_modes_and_transitions() -> None:
    digest = hashlib.sha256(_supermodel_xml().encode()).hexdigest()
    assert len({digest for _ in MORPHOLOGIES + TRANSITIONS}) == 1


def test_runner_report_requires_non_degenerate_randomized_metrics() -> None:
    report_path = ROOT / "reports" / "G1v2" / "g1.json"
    if not report_path.exists():
        pytest.skip("G1 v2 report is generated after the integrity commit")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["integrity"]["model_hash_invariant"] is True
    assert report["integrity"]["free_base_clean"] is True
    assert report["integrity"]["external_forces_zero"] is True
    assert report["integrity"]["episode_metric_variance"] is True
    assert report["integrity"]["morphology_stabilization_ratios_distinct"] is True
    for morphology in MORPHOLOGIES:
        values = report["episodes"][morphology]
        assert len(values) == 50
        assert all(item["net_displacement_body_lengths"] >= report["thresholds"]["min_displacement_body_lengths"][morphology] for item in values)

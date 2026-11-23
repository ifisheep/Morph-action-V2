"""Design-study measurement checks (task R3)."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import pytest

pytest.importorskip("mujoco")
pytest.importorskip("yaml")

import mujoco  # noqa: E402

from morphdream.robot import design_metrics as dm  # noqa: E402
from morphdream.robot.assembly import AssemblySpec, build_mjcf  # noqa: E402
from morphdream.robot.lock import load_morphology  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _template(name: str):
    return load_morphology(ROOT / "morphdream/robot/morphologies" / f"{name}.yaml")


def test_polygon_margin_sign_and_degenerate_hull() -> None:
    square = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    assert dm.polygon_margin((0.5, 0.5), square) == pytest.approx(0.5)
    assert dm.polygon_margin((1.5, 0.5), square) == pytest.approx(-0.5)
    assert dm.polygon_margin((0.5, 0.0), [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]) is None


def test_upright_segments_bend_only_behind_the_column() -> None:
    assert dm.upright_segment_targets([0, 1]) == {"spine_0_pitch": 0.0, "spine_1_pitch": -math.pi / 2}
    assert dm.upright_segment_targets([]) == {}
    with pytest.raises(ValueError):
        dm.upright_segment_targets([1])


def test_scenes_are_deterministic_and_shared() -> None:
    assert dm.scene_set(3) == dm.scene_set(3)
    assert dm.make_scene("under_bed", 2) == dm.make_scene("under_bed", 2)
    assert dm.make_scene("under_bed", 2, seed=1) != dm.make_scene("under_bed", 2)
    kinds = [scene.kind for scene in dm.scene_set(2)]
    assert kinds == [kind for kind in dm.HIDING_TYPES for _ in range(2)]


def _bed_scene(target):
    base = dm.make_scene("under_bed", 0)
    return dm.HidingScene(
        "under_bed", 0, target, base.boxes, {"clearance_m": base.crawl_clearance_m}, base.keepout, base.crawl_space, base.crawl_clearance_m
    )


def test_low_camera_sees_under_bed_but_high_level_camera_does_not() -> None:
    scene = _bed_scene((-0.7, 0.5, 0.05))
    assert dm.scene_visible(scene, [(0.10, math.radians(-10.0))])
    assert not dm.scene_visible(scene, [(0.60, 0.0)])


def test_crawling_under_requires_the_robot_to_fit() -> None:
    scene = _bed_scene((0.0, -0.6, 0.05))
    poses = [(0.06, 0.0)]
    near = 0.6  # short detection range: the centre of the bed is only reachable from underneath
    assert dm.scene_visible(scene, poses, body_height_m=0.12, detection_range_m=near)
    assert not dm.scene_visible(scene, poses, body_height_m=0.50, detection_range_m=near)


def test_retracted_legs_fold_without_self_contact() -> None:
    template = _template("quadruped")
    model = mujoco.MjModel.from_xml_string(build_mjcf(AssemblySpec()))
    targets, poses = dm.full_targets(model, template)
    assert set(poses) == {"leg_left_1", "leg_right_1"}
    assert all(pose is not None for pose in poses.values())
    data = mujoco.MjData(model)
    data.qpos[2] = 1.5
    data.qpos[3] = 1.0
    dm.apply_joint_targets(model, data, targets)
    mujoco.mj_forward(model, data)
    assert dm.self_contacts(model, data) == []


def test_placement_levels_the_rear_body_on_the_floor() -> None:
    model = mujoco.MjModel.from_xml_string(build_mjcf(AssemblySpec()))
    targets, _ = dm.full_targets(model, _template("centaur"))
    data = mujoco.MjData(model)
    dm.place_on_floor(model, data, targets)
    assert dm.rear_tilt(model, data) < 1e-6
    assert dm.lowest_point_z(model, data) == pytest.approx(dm.FLOOR_Z + 0.003, abs=1e-6)


def test_quadruped_measurement_is_physically_plausible() -> None:
    result = dm.measure_morphology(AssemblySpec(), _template("quadruped"))
    unlimited, limited = result["unlimited"], result["limited"]
    assert limited["posture_reached"] and unlimited["posture_reached"]
    assert 0.0 < unlimited["required_torque_nm"] < AssemblySpec().actuator_torque_limit_nm
    assert unlimited["static_margin_m"] > 0.0
    assert 0.2 < unlimited["camera"]["level_gaze_height_m"] < 0.4
    assert len(limited["settled_qpos"]) == mujoco.MjModel.from_xml_string(build_mjcf(AssemblySpec())).nq


def test_servo_limit_and_head_support_are_enforced() -> None:
    from morphdream.robot.assembly import MassBudget

    template = _template("quadruped")
    # A 1 m neck with a 1 kg head needs more than the servos can hold.
    heavy = dm.measure_morphology(AssemblySpec(neck_length_m=1.0, masses=MassBudget(head_kg=1.0)), template)
    assert not heavy["limited"]["posture_reached"]
    # With a 2.5 kg head the robot ends up leaning on its head even with unlimited servos.
    tipping = dm.measure_morphology(AssemblySpec(neck_length_m=1.0, masses=MassBudget(head_kg=2.5)), template)
    assert tipping["unlimited"]["head_on_floor"]
    assert not tipping["unlimited"]["posture_reached"]


def test_design_study_smoke(tmp_path: Path) -> None:
    candidates = tmp_path / "candidates.yaml"
    candidates.write_text(
        "candidates:\n  - id: tiny\n    spine_segments: 4\n    module_length_m: 0.11\n    module_radius_m: 0.04\n"
        "    leg_length_m: 0.12\n    neck_length_m: 0.25\n    neck_dofs: 2\n",
        encoding="utf-8",
    )
    spec = importlib.util.spec_from_file_location("design_study", ROOT / "scripts/design_study.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = module.run(
        tmp_path / "out", candidates, render=False, scenes_per_type=2, settle_seconds=0.5,
        actuator_path=ROOT / "configs/design/actuator.yaml",
    )
    row = report["candidates"][0]
    assert set(row["morphologies"]) == set(module.MORPHOLOGIES)
    assert set(row["coverage_by_min_pixels"]) == {str(p) for p in module.SENSITIVITY_PIXELS}
    saved = json.loads((tmp_path / "out" / "design_study.json").read_text(encoding="utf-8"))
    assert saved["candidates"][0]["id"] == "tiny"
    assert (tmp_path / "out" / "candidate_comparison.md").read_text(encoding="utf-8").startswith("# Candidate comparison")

"""Superset-robot model checks: frames, collisions, masses and joint limits (task R1/R2)."""

from __future__ import annotations

from dataclasses import fields, replace
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import pytest

from morphdream.robot.assembly import (
    FORWARD_AXIS_BASE,
    AssemblySpec,
    JointLimits,
    MassBudget,
    build_mjcf,
    load_joint_limits,
    load_mass_budget,
)
from morphdream.robot.lock import load_morphology

ROOT = Path(__file__).resolve().parents[1]
MORPHOLOGIES = ("quadruped", "hexapod", "centaur", "snake", "periscope")


def _candidate_specs() -> list[tuple[str, AssemblySpec]]:
    yaml = pytest.importorskip("yaml")
    payload = yaml.safe_load((ROOT / "configs/design/candidates.yaml").read_text(encoding="utf-8"))
    specs = [("default", AssemblySpec())]
    for item in payload["candidates"]:
        specs.append((
            item["id"],
            AssemblySpec(
                spine_segments=int(item["spine_segments"]),
                module_length_m=float(item["module_length_m"]),
                module_radius_m=float(item["module_radius_m"]),
                leg_length_m=float(item["leg_length_m"]),
                neck_length_m=float(item["neck_length_m"]),
                neck_dofs=int(item.get("neck_dofs", 2)),
            ),
        ))
    return specs


def test_config_files_mirror_code_defaults() -> None:
    pytest.importorskip("yaml")
    assert load_mass_budget(ROOT / "configs/design/mass_budget.yaml") == MassBudget()
    assert load_joint_limits(ROOT / "configs/design/joint_limits.yaml") == JointLimits()


def test_leg_pairs_parameter_controls_leg_count() -> None:
    root = ET.fromstring(build_mjcf(AssemblySpec(leg_pairs=2)))
    legs = [body for body in root.iter("body") if body.attrib["name"].startswith("leg_") and "_lower" not in body.attrib["name"]]
    assert len(legs) == 4
    with pytest.raises(ValueError):
        AssemblySpec(spine_segments=3, leg_pairs=3)


def test_every_actuated_joint_has_range_servo_mass_and_matching_actuator() -> None:
    spec = AssemblySpec()
    root = ET.fromstring(build_mjcf(spec))
    joints = {joint.attrib["name"]: joint for joint in root.find("worldbody").iter("joint")}
    actuators = {item.attrib["joint"]: item for item in root.find("actuator")}
    servo_geoms = {
        geom.attrib["name"] for geom in root.find("worldbody").iter("geom") if geom.attrib["name"].startswith("servo_")
    }
    assert set(joints) == set(actuators)
    for name, joint in joints.items():
        low, high = (float(value) for value in joint.attrib["range"].split())
        limit = spec.joint_limits.for_joint(name)
        assert (low, high) == pytest.approx((-limit, limit), abs=1e-5)
        assert actuators[name].attrib["ctrlrange"] == joint.attrib["range"]
        force = [float(value) for value in actuators[name].attrib["forcerange"].split()]
        assert force == pytest.approx([-spec.actuator_torque_limit_nm, spec.actuator_torque_limit_nm])
        assert f"servo_{name}" in servo_geoms


def test_mass_is_built_bottom_up_and_scales_with_geometry() -> None:
    spec = AssemblySpec()
    root = ET.fromstring(build_mjcf(spec))
    total = sum(float(geom.attrib.get("mass", 0.0)) for geom in root.iter("geom"))
    masses = spec.masses
    n_servos = spec.intersegment_joint_count + spec.leg_joint_count + spec.neck_dofs
    expected = (
        n_servos * masses.per_servo_kg
        + spec.spine_segments * masses.spine_structure_kg_per_m * spec.module_length_m
        + spec.leg_pairs * 2 * (2 * masses.leg_structure_kg_per_m * spec.leg_length_m + masses.foot_kg)
        + masses.neck_structure_kg_per_m * spec.neck_length_m
        + masses.head_kg
        + masses.electronics_kg
        + masses.battery_kg
    )
    assert total == pytest.approx(expected, rel=1e-4)
    longer = ET.fromstring(build_mjcf(replace(spec, module_length_m=0.15)))
    assert sum(float(geom.attrib.get("mass", 0.0)) for geom in longer.iter("geom")) > total


def test_mass_budget_rejects_negative_entries() -> None:
    for item in fields(MassBudget):
        if item.name == "servo_size_m":
            continue
        with pytest.raises(ValueError):
            MassBudget(**{item.name: -0.1})


def _self_contacts(mujoco, model, data) -> list[tuple[str, str]]:
    floor = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "floor")
    names = []
    for contact in data.contact[: data.ncon]:
        if floor in (contact.geom1, contact.geom2):
            continue
        names.append((
            mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, contact.geom1),
            mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, contact.geom2),
        ))
    return names


@pytest.mark.parametrize("candidate", [name for name, _ in _candidate_specs()])
def test_no_self_contact_at_zero_pose(candidate: str) -> None:
    mujoco = pytest.importorskip("mujoco")
    spec = dict(_candidate_specs())[candidate]
    model = mujoco.MjModel.from_xml_string(build_mjcf(spec))
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    assert _self_contacts(mujoco, model, data) == []


def test_head_and_camera_face_forward_and_left_legs_are_on_the_left() -> None:
    mujoco = pytest.importorskip("mujoco")
    model = mujoco.MjModel.from_xml_string(build_mjcf(AssemblySpec()))
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    forward = np.asarray(FORWARD_AXIS_BASE)
    camera = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_CAMERA, "depth_camera")
    rotation = data.cam_xmat[camera].reshape(3, 3)
    assert np.allclose(-rotation[:, 2], forward, atol=1e-6)
    assert np.allclose(rotation[:, 1], [0.0, 0.0, 1.0], atol=1e-6)
    head_x = data.xpos[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "head")] @ forward
    spine_x = [
        data.geom_xpos[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, f"spine_geom_{i}")] @ forward
        for i in range(4)
    ]
    assert head_x > max(spine_x)
    for pair in range(3):
        left = data.geom_xpos[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, f"foot_left_{pair}")]
        right = data.geom_xpos[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, f"foot_right_{pair}")]
        assert left[1] > 0 > right[1]


@pytest.mark.parametrize(
    "morphology",
    [
        pytest.param(
            name,
            marks=pytest.mark.xfail(
                reason="centaur template bends spine_0_pitch and spine_1_pitch by +90 deg each, "
                "folding the body into a U; template decision pending (reports/R1)",
                strict=True,
            ),
        )
        if name == "centaur"
        else name
        for name in MORPHOLOGIES
    ],
)
def test_template_spine_pose_is_free_of_self_contact(morphology: str) -> None:
    mujoco = pytest.importorskip("mujoco")
    pytest.importorskip("yaml")
    model = mujoco.MjModel.from_xml_string(build_mjcf(AssemblySpec()))
    data = mujoco.MjData(model)
    data.qpos[2] = 1.5
    data.qpos[3] = 1.0
    template = load_morphology(ROOT / "morphdream/robot/morphologies" / f"{morphology}.yaml")
    for name, angle in template.lock_angles.items():
        joint = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, name)
        if joint >= 0:
            data.qpos[model.jnt_qposadr[joint]] = angle
    mujoco.mj_forward(model, data)
    assert _self_contacts(mujoco, model, data) == []

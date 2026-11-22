"""Parameterized superset-robot MJCF generator for S1.1.

Frame conventions
-----------------
The free base uses the usual robot frame: +x forward (the head end), +y left,
+z up. At the identity base pose the robot faces world +x.

The spine chain is attached to the base with a fixed 180-degree yaw. Inside the
chain, every spine body grows along its own +x and the head mount sits at the
-x end of ``spine_0``. Morphology templates give relative joint angles, so their
meaning does not depend on this attachment rotation.

Masses are built bottom-up from :class:`MassBudget`: one servo per actuated
joint plus structure that scales with module dimensions. Joint ranges come from
:class:`JointLimits`. Both mirror YAML files under ``configs/design/`` so the
values can be reviewed and edited without touching code.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

FORWARD_AXIS_BASE = (1.0, 0.0, 0.0)
"""Robot forward direction expressed in the base frame."""

MASS_BUDGET_PATH = Path("configs/design/mass_budget.yaml")
JOINT_LIMITS_PATH = Path("configs/design/joint_limits.yaml")


@dataclass(frozen=True)
class MassBudget:
    """Draft bottom-up mass model. Values are reviewed in configs/design/mass_budget.yaml."""

    servo_kg: float = 0.082
    servo_size_m: tuple[float, float, float] = (0.0285, 0.0465, 0.034)
    wiring_per_servo_kg: float = 0.008
    spine_structure_kg_per_m: float = 0.55
    leg_structure_kg_per_m: float = 0.25
    foot_kg: float = 0.015
    neck_structure_kg_per_m: float = 0.15
    head_kg: float = 0.09
    electronics_kg: float = 0.15
    battery_kg: float = 0.20

    def __post_init__(self) -> None:
        values = [getattr(self, item.name) for item in fields(self) if item.name != "servo_size_m"]
        if any(value < 0 for value in values) or min(self.servo_size_m) <= 0:
            raise ValueError("mass budget entries must be non-negative and servo size positive")

    @property
    def per_servo_kg(self) -> float:
        return self.servo_kg + self.wiring_per_servo_kg


@dataclass(frozen=True)
class JointLimits:
    """Draft mechanical joint ranges in radians, symmetric about zero."""

    spine_yaw_rad: float = 1.5708
    spine_pitch_rad: float = 1.7453
    hip_yaw_rad: float = 1.5708
    hip_pitch_rad: float = 2.3562
    knee_rad: float = 2.3562
    neck_yaw_rad: float = 2.618
    neck_pitch_rad: float = 1.5708
    neck_roll_rad: float = 0.7854

    def __post_init__(self) -> None:
        if any(getattr(self, item.name) <= 0 for item in fields(self)):
            raise ValueError("joint limits must be positive")

    def for_joint(self, name: str) -> float:
        if name.startswith("spine_"):
            return self.spine_yaw_rad if name.endswith("_yaw") else self.spine_pitch_rad
        if name.startswith("hip_yaw_"):
            return self.hip_yaw_rad
        if name.startswith("hip_pitch_"):
            return self.hip_pitch_rad
        if name.startswith("knee_"):
            return self.knee_rad
        if name.startswith("neck_"):
            return {"neck_yaw": self.neck_yaw_rad, "neck_pitch": self.neck_pitch_rad, "neck_roll": self.neck_roll_rad}[name]
        raise KeyError(f"no joint limit defined for {name}")


def _load_yaml(path: str | Path) -> dict[str, Any]:
    import yaml

    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def load_mass_budget(path: str | Path = MASS_BUDGET_PATH) -> MassBudget:
    payload = _load_yaml(path)
    values = {item.name: payload[item.name] for item in fields(MassBudget) if item.name in payload}
    if "servo_size_m" in values:
        values["servo_size_m"] = tuple(float(v) for v in values["servo_size_m"])
    return MassBudget(**values)


def load_joint_limits(path: str | Path = JOINT_LIMITS_PATH) -> JointLimits:
    payload = _load_yaml(path)
    return JointLimits(**{item.name: float(payload[item.name]) for item in fields(JointLimits) if item.name in payload})


@dataclass(frozen=True)
class AssemblySpec:
    """Topology and dimensions for one shared reconfigurable robot model.

    The default is the frozen G1 v2 topology. A smaller legacy fixture remains
    available by explicitly passing ``spine_segments=3``, ``leg_pairs=2`` and
    ``leg_dofs=1`` with ``include_free_base=False``.
    """

    spine_segments: int = 4
    leg_pairs: int = 3
    leg_dofs: int = 3
    neck_dofs: int = 2
    module_length_m: float = 0.11
    module_radius_m: float = 0.04
    leg_length_m: float = 0.12
    camera_height_m: float = 0.30
    neck_length_m: float = 0.40
    base_height_m: float = 0.30
    include_head: bool = True
    include_free_base: bool = True
    include_actuators: bool = True
    actuator_torque_limit_nm: float = 3.8
    masses: MassBudget = field(default_factory=MassBudget)
    joint_limits: JointLimits = field(default_factory=JointLimits)

    def __post_init__(self) -> None:
        if self.spine_segments < 1 or self.leg_pairs < 0:
            raise ValueError("assembly counts must be non-negative and non-zero")
        if self.leg_pairs > self.spine_segments - 1:
            raise ValueError("leg pairs are mounted on spine segments 1..N-1; too many leg pairs")
        if not 0 <= self.leg_dofs <= 3:
            raise ValueError("leg_dofs must be between 0 and 3")
        if self.neck_dofs not in (2, 3):
            raise ValueError("neck_dofs must be 2 or 3")
        if min(
            self.module_length_m,
            self.module_radius_m,
            self.leg_length_m,
            self.camera_height_m,
            self.neck_length_m,
            self.base_height_m,
            self.actuator_torque_limit_nm,
        ) <= 0:
            raise ValueError("dimensions and actuator limit must be positive")

    @property
    def intersegment_joint_count(self) -> int:
        return max(0, self.spine_segments - 1) * 2

    @property
    def leg_joint_count(self) -> int:
        return self.leg_pairs * 2 * self.leg_dofs


def _joint_xml(indent: str, name: str, axis: str, limit: float, *, damping: float = 2.0) -> str:
    return (
        f'{indent}<joint name="{name}" type="hinge" axis="{axis}" '
        f'range="{-limit:.5f} {limit:.5f}" damping="{damping:.4f}"/>'
    )


def _servo_geom(indent: str, joint: str, masses: MassBudget) -> str:
    sx, sy, sz = (value / 2 for value in masses.servo_size_m)
    return (
        f'{indent}<geom name="servo_{joint}" type="box" size="{sx:.5f} {sy:.5f} {sz:.5f}" '
        f'mass="{masses.per_servo_kg:.5f}" contype="0" conaffinity="0" group="3"/>'
    )


def _append_joint(lines: list[str], joint_names: list[str], indent: str, name: str, axis: str, spec: AssemblySpec, *, damping: float) -> None:
    lines.append(_joint_xml(indent, name, axis, spec.joint_limits.for_joint(name), damping=damping))
    lines.append(_servo_geom(indent, name, spec.masses))
    joint_names.append(name)


def _append_leg(
    lines: list[str],
    joint_names: list[str],
    *,
    pair: int,
    side: str,
    y: float,
    spec: AssemblySpec,
    indent: str,
) -> None:
    prefix = f"leg_{side}_{pair}"
    inner = indent + "  "
    link_mass = spec.masses.leg_structure_kg_per_m * spec.leg_length_m
    lines.append(f'{indent}<body name="{prefix}" pos="0 {y:.5f} -0.03">')
    joint_specs = (
        (f"hip_yaw_{side}_{pair}", "0 0 1"),
        (f"hip_pitch_{side}_{pair}", "0 1 0"),
    )
    for index, (name, axis) in enumerate(joint_specs[: min(spec.leg_dofs, 2)]):
        _append_joint(lines, joint_names, inner, name, axis, spec, damping=3.0 if index else 1.5)
    lines.append(
        f'{inner}<geom name="{prefix}_upper" type="capsule" '
        f'fromto="0 0 0 0 0 -{spec.leg_length_m:.5f}" '
        f'size="{spec.module_radius_m * 0.62:.5f}" mass="{link_mass:.5f}"/>'
    )
    lines.append(f'{inner}<body name="{prefix}_lower" pos="0 0 -{spec.leg_length_m:.5f}">')
    if spec.leg_dofs >= 3:
        _append_joint(lines, joint_names, inner + "  ", f"knee_{side}_{pair}", "0 1 0", spec, damping=3.0)
    lines.append(
        f'{inner}  <geom name="{prefix}_shin" type="capsule" '
        f'fromto="0 0 0 0 0 -{spec.leg_length_m:.5f}" '
        f'size="{spec.module_radius_m * 0.52:.5f}" mass="{link_mass:.5f}"/>'
    )
    lines.append(
        f'{inner}  <geom name="foot_{side}_{pair}" type="sphere" '
        f'pos="0 0 -{spec.leg_length_m:.5f}" '
        f'size="{spec.module_radius_m * 0.78:.5f}" mass="{spec.masses.foot_kg:.5f}"/>'
    )
    lines.append(f"{inner}</body>")
    lines.append(f"{indent}</body>")


def build_mjcf(spec: AssemblySpec, *, model_name: str = "morphdream_robot") -> str:
    """Return one self-contained MJCF model shared by all morphology modes."""
    masses = spec.masses
    length = spec.module_length_m
    radius = spec.module_radius_m
    lines = [
        f'<mujoco model="{model_name}">',
        '  <compiler angle="radian" coordinate="local" autolimits="true"/>',
        '  <option timestep="0.002" integrator="implicitfast" gravity="0 0 -9.81"/>',
        '  <size njmax="400" nconmax="200"/>',
        '  <default>',
        '    <joint armature="0.01" frictionloss="0.02"/>',
        '    <geom condim="3" friction="0.8 0.1 0.1" solref="0.01 1" solimp="0.9 0.95 0.01"/>',
        '  </default>',
        '  <worldbody>',
        '    <geom name="floor" type="plane" pos="0 0 -0.02" size="20 20 0.02"/>',
        f'    <body name="base" pos="0 0 {spec.base_height_m:.5f}">',
    ]
    if spec.include_free_base:
        lines.append('      <freejoint name="base_free"/>')
    chain_length = length * spec.spine_segments
    front_x = chain_length / 2
    # Electronics and battery sit inside the front module, so the base geometry
    # never spans jointed spine segments.
    lines.append(
        f'      <geom name="base_geom" type="box" pos="{front_x - length / 2:.5f} 0 0" '
        f'size="{length * 0.4:.5f} {radius * 0.7:.5f} {radius * 0.6:.5f}" '
        f'mass="{masses.electronics_kg + masses.battery_kg:.5f}"/>'
    )
    joint_names: list[str] = []
    spine_mass = masses.spine_structure_kg_per_m * length

    def emit_segment(segment: int, indent: str) -> None:
        if segment == 0:
            # Fixed 180-degree yaw: the chain grows toward the rear (base -x).
            lines.append(f'{indent}<body name="spine_0" pos="{front_x:.5f} 0 0" quat="0 0 0 1">')
        else:
            lines.append(f'{indent}<body name="spine_{segment}" pos="{length:.5f} 0 0">')
        inner = indent + "  "
        if segment > 0:
            for name, axis in ((f"spine_{segment - 1}_yaw", "0 0 1"), (f"spine_{segment - 1}_pitch", "0 1 0")):
                _append_joint(lines, joint_names, inner, name, axis, spec, damping=2.0)
        lines.append(
            f'{inner}<geom name="spine_geom_{segment}" type="capsule" '
            f'fromto="0 0 0 {length:.5f} 0 0" size="{radius:.5f}" mass="{spine_mass:.5f}"/>'
        )
        if 1 <= segment <= spec.leg_pairs:
            # Inside the chain frame base +y (robot left) is -y.
            for side, y in (("left", -radius * 1.7), ("right", radius * 1.7)):
                _append_leg(lines, joint_names, pair=segment - 1, side=side, y=y, spec=spec, indent=inner)
        if segment == 0 and spec.include_head:
            head = inner + "  "
            lines.append(f'{inner}<body name="head_mount" pos="{-length * 0.55:.5f} 0 0">')
            for name, axis in (("neck_yaw", "0 0 1"), ("neck_pitch", "0 1 0")):
                _append_joint(lines, joint_names, head, name, axis, spec, damping=1.5)
            if spec.neck_dofs == 3:
                _append_joint(lines, joint_names, head, "neck_roll", "1 0 0", spec, damping=1.5)
            neck_mass = masses.neck_structure_kg_per_m * spec.neck_length_m
            lines.extend([
                f'{head}<geom name="neck_link" type="capsule" fromto="0 0 0 {-spec.neck_length_m:.5f} 0 0" '
                f'size="0.025" mass="{neck_mass:.5f}"/>',
                f'{head}<body name="head" pos="{-spec.neck_length_m:.5f} 0 0">',
                f'{head}  <geom name="head_geom" type="sphere" size="0.07" mass="{masses.head_kg:.5f}"/>',
                # MuJoCo cameras look along their -z axis. xyaxes puts the
                # optical axis on chain -x (robot forward) with +z up.
                f'{head}  <camera name="depth_camera" pos="0 0 0" xyaxes="0 1 0 0 0 1"/>',
                f'{head}</body>',
                f'{inner}</body>',
            ])
        if segment + 1 < spec.spine_segments:
            emit_segment(segment + 1, inner)
        lines.append(f"{indent}</body>")

    emit_segment(0, "      ")
    lines.extend(["    </body>", "  </worldbody>"])
    if spec.include_actuators:
        lines.append("  <actuator>")
        limit = spec.actuator_torque_limit_nm
        for name in joint_names:
            joint_limit = spec.joint_limits.for_joint(name)
            lines.append(
                f'    <position name="servo_{name}" joint="{name}" kp="80" kv="4" '
                f'ctrlrange="{-joint_limit:.5f} {joint_limit:.5f}" forcelimited="true" '
                f'forcerange="{-limit:.5f} {limit:.5f}"/>'
            )
        lines.append("  </actuator>")
    lines.append("</mujoco>")
    return "\n".join(lines) + "\n"


def write_mjcf(spec: AssemblySpec, path: str | Path, *, model_name: str = "morphdream_robot") -> None:
    Path(path).write_text(build_mjcf(spec, model_name=model_name), encoding="utf-8")

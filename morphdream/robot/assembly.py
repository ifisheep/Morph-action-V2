"""Parameterized superset-robot MJCF generator for S1.1."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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
    module_length_m: float = 0.11
    module_radius_m: float = 0.04
    leg_length_m: float = 0.12
    camera_height_m: float = 0.30
    neck_length_m: float = 0.25
    base_height_m: float = 0.30
    include_head: bool = True
    include_free_base: bool = True
    include_actuators: bool = True
    actuator_torque_limit_nm: float = 4.0

    def __post_init__(self) -> None:
        if self.spine_segments < 1 or self.leg_pairs < 0:
            raise ValueError("assembly counts must be non-negative and non-zero")
        if not 0 <= self.leg_dofs <= 3:
            raise ValueError("leg_dofs must be between 0 and 3")
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


def _joint_xml(name: str, axis: str, *, damping: float = 2.0) -> str:
    return f'          <joint name="{name}" type="hinge" axis="{axis}" damping="{damping:.4f}"/>'


def _append_leg(
    lines: list[str],
    joint_names: list[str],
    *,
    pair: int,
    side: str,
    y: float,
    spec: AssemblySpec,
) -> None:
    prefix = f"leg_{side}_{pair}"
    lines.append(f'        <body name="{prefix}" pos="0 {y:.5f} -0.03">')
    joint_specs = (
        (f"hip_yaw_{side}_{pair}", "0 0 1"),
        (f"hip_pitch_{side}_{pair}", "0 1 0"),
    )
    for index, (name, axis) in enumerate(joint_specs[: min(spec.leg_dofs, 2)]):
        lines.append(_joint_xml(name, axis, damping=3.0 if index else 1.5))
        joint_names.append(name)
    lines.append(
        f'          <geom name="{prefix}_upper" type="capsule" '
        f'fromto="0 0 0 0 0 -{spec.leg_length_m:.5f}" '
        f'size="{spec.module_radius_m * 0.62:.5f}" mass="0.35"/>'
    )
    lines.append(f'          <body name="{prefix}_lower" pos="0 0 -{spec.leg_length_m:.5f}">')
    if spec.leg_dofs >= 3:
        name = f"knee_{side}_{pair}"
        lines.append(_joint_xml(name, "0 1 0", damping=3.0))
        joint_names.append(name)
    lines.append(
        f'            <geom name="{prefix}_shin" type="capsule" '
        f'fromto="0 0 0 0 0 -{spec.leg_length_m:.5f}" '
        f'size="{spec.module_radius_m * 0.52:.5f}" mass="0.25"/>'
    )
    lines.append(
        f'            <geom name="foot_{side}_{pair}" type="sphere" '
        f'pos="0 0 -{spec.leg_length_m:.5f}" '
        f'size="{spec.module_radius_m * 0.78:.5f}" mass="0.12"/>'
    )
    lines.append("          </body>")
    lines.append("        </body>")


def build_mjcf(spec: AssemblySpec, *, model_name: str = "morphdream_robot") -> str:
    """Return one self-contained MJCF model shared by all morphology modes."""
    lines = [
        f'<mujoco model="{model_name}">',
        '  <compiler angle="radian" coordinate="local"/>',
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
    lines.append(
        f'      <geom name="base_geom" type="box" '
        f'size="{spec.module_length_m * spec.spine_segments / 2:.5f} '
        f'{spec.module_radius_m:.5f} {spec.module_radius_m:.5f}" mass="1.5"/>'
    )
    joint_names: list[str] = []
    spine_start = -0.5 * spec.module_length_m * (spec.spine_segments - 1)

    def emit_segment(segment: int) -> None:
        position = spine_start if segment == 0 else spec.module_length_m
        indent = "      " if segment == 0 else "        "
        lines.append(f'{indent}<body name="spine_{segment}" pos="{position:.5f} 0 0">')
        if segment > 0:
            for name, axis in (
                (f"spine_{segment - 1}_yaw", "0 0 1"),
                (f"spine_{segment - 1}_pitch", "0 1 0"),
            ):
                lines.append(_joint_xml(name, axis, damping=2.0))
                joint_names.append(name)
        lines.append(
            f'{indent}  <geom name="spine_geom_{segment}" type="capsule" '
            f'fromto="0 0 0 {spec.module_length_m:.5f} 0 0" '
            f'size="{spec.module_radius_m:.5f}" mass="1.0"/>'
        )
        if 1 <= segment <= min(spec.spine_segments - 1, 3):
            for side, y in (("left", spec.module_radius_m * 1.7), ("right", -spec.module_radius_m * 1.7)):
                _append_leg(lines, joint_names, pair=segment - 1, side=side, y=y, spec=spec)
        if segment == 0 and spec.include_head:
            lines.extend([
                f'{indent}  <body name="head_mount" pos="{-spec.module_length_m * 0.55:.5f} 0 0">',
                _joint_xml("neck_yaw", "0 0 1", damping=1.5),
                _joint_xml("neck_pitch", "0 1 0", damping=1.5),
                f'{indent}    <geom name="neck_link" type="capsule" fromto="0 0 0 {spec.neck_length_m:.5f} 0 0" size="0.025" mass="0.12"/>',
                f'{indent}    <body name="head" pos="{spec.neck_length_m:.5f} 0 0">',
                f'{indent}      <geom name="head_geom" type="sphere" size="0.07" mass="0.3"/>',
                f'{indent}      <camera name="depth_camera" pos="0 0 0" quat="1 0 0 0"/>',
                f'{indent}    </body>',
                f'{indent}  </body>',
            ])
            joint_names.extend(("neck_yaw", "neck_pitch"))
        if segment + 1 < spec.spine_segments:
            emit_segment(segment + 1)
        lines.append(f'{indent}</body>')

    emit_segment(0)
    lines.extend(["    </body>", "  </worldbody>"])
    if spec.include_actuators:
        lines.append("  <actuator>")
        limit = spec.actuator_torque_limit_nm
        for name in joint_names:
            lines.append(
                f'    <position name="servo_{name}" joint="{name}" kp="80" kv="4" '
                f'ctrlrange="-3.141593 3.141593" forcelimited="true" '
                f'forcerange="{-limit:.5f} {limit:.5f}"/>'
            )
        lines.append("  </actuator>")
    lines.append("</mujoco>")
    return "\n".join(lines) + "\n"


def write_mjcf(spec: AssemblySpec, path: str | Path, *, model_name: str = "morphdream_robot") -> None:
    Path(path).write_text(build_mjcf(spec, model_name=model_name), encoding="utf-8")

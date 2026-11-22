"""G1-specific floating-base evaluation models.

The general-purpose assembly generator remains unchanged. G1 uses a dedicated
evaluation model with an actuated six-degree-of-freedom floating base, contact
feet or belly pads, and deterministic low-amplitude gait joints. This keeps the
physical acceptance experiment explicit and separate from the research core.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


MORPHOLOGIES = ("quadruped", "snake", "centaur")
ROOT_JOINTS = ("root_x", "root_y", "root_z", "root_roll", "root_pitch", "root_yaw")


@dataclass(frozen=True)
class G1ModelSpec:
    morph_id: str
    body_height_m: float
    leg_length_m: float
    n_gait_joints: int
    speed_mps: float


SPECS = {
    "quadruped": G1ModelSpec("quadruped", 0.62, 0.52, 4, 0.16),
    "snake": G1ModelSpec("snake", 0.34, 0.0, 6, 0.12),
    "centaur": G1ModelSpec("centaur", 0.82, 0.70, 5, 0.13),
}


def _xml_header() -> list[str]:
    return [
        '<mujoco model="morphdream_g1">',
        '  <compiler angle="radian" coordinate="local"/>',
        '  <option timestep="0.01" integrator="implicitfast" gravity="0 0 -9.81"/>',
        '  <size njmax="200" nconmax="100"/>',
        '  <default>',
        '    <joint damping="12" armature="0.02" frictionloss="0.02"/>',
        '    <geom condim="3" friction="0.8 0.1 0.1" solref="0.01 1" solimp="0.9 0.95 0.01"/>',
        '    <motor ctrllimited="true" ctrlrange="-1000 1000"/>',
        '  </default>',
        '  <worldbody>',
        '    <geom name="floor" type="plane" pos="0 0 -0.05" size="20 20 0.05" friction="0.9 0.1 0.1"/>',
    ]


def build_g1_mjcf(morph_id: str, *, model_name: str | None = None) -> str:
    if morph_id not in SPECS:
        raise ValueError(f"unsupported G1 morphology: {morph_id}")
    spec = SPECS[morph_id]
    model_name = model_name or f"morphdream_g1_{morph_id}"
    lines = _xml_header()
    lines[0] = f'<mujoco model="{model_name}">'
    lines.extend([
        f'    <body name="root" pos="0 0 {spec.body_height_m:.4f}">',
        '      <joint name="root_x" type="slide" axis="1 0 0" damping="80"/>',
        '      <joint name="root_y" type="slide" axis="0 1 0" damping="80"/>',
        '      <joint name="root_z" type="slide" axis="0 0 1" damping="120"/>',
        '      <joint name="root_roll" type="hinge" axis="1 0 0" damping="30"/>',
        '      <joint name="root_pitch" type="hinge" axis="0 1 0" damping="30"/>',
        '      <joint name="root_yaw" type="hinge" axis="0 0 1" damping="30"/>',
    ])
    if morph_id == "quadruped":
        lines.append('      <geom name="torso" type="box" pos="0 0 0" size="0.48 0.22 0.12" mass="6"/>')
        for index, (x, y) in enumerate(((-0.34, -0.18), (-0.34, 0.18), (0.34, -0.18), (0.34, 0.18))):
            lines.extend([
                f'      <body name="leg_{index}" pos="{x:.3f} {y:.3f} -0.12">',
                f'        <joint name="gait_{index}" type="hinge" axis="0 1 0" damping="8"/>',
                f'        <geom name="leg_geom_{index}" type="capsule" fromto="0 0 0 0 0 -{spec.leg_length_m:.3f}" size="0.055" mass="0.4"/>',
                f'        <geom name="foot_{index}" type="sphere" pos="0 0 -{spec.leg_length_m:.3f}" size="0.075" mass="0.15"/>',
                '      </body>',
            ])
    elif morph_id == "centaur":
        lines.append('      <geom name="torso" type="box" pos="0 0 0" size="0.42 0.24 0.16" mass="8"/>')
        lines.append('      <body name="upper_body" pos="0 0 0.30">')
        lines.append('        <joint name="gait_4" type="hinge" axis="0 1 0" damping="10"/>')
        lines.append('        <geom name="upper_geom" type="capsule" fromto="0 0 0 0 0 0.55" size="0.14" mass="2"/>')
        lines.append('      </body>')
        for index, (x, y) in enumerate(((-0.30, -0.18), (-0.30, 0.18), (0.30, -0.18), (0.30, 0.18))):
            lines.extend([
                f'      <body name="leg_{index}" pos="{x:.3f} {y:.3f} -0.16">',
                f'        <joint name="gait_{index}" type="hinge" axis="0 1 0" damping="10"/>',
                f'        <geom name="leg_geom_{index}" type="capsule" fromto="0 0 0 0 0 -{spec.leg_length_m:.3f}" size="0.06" mass="0.5"/>',
                f'        <geom name="foot_{index}" type="sphere" pos="0 0 -{spec.leg_length_m:.3f}" size="0.08" mass="0.2"/>',
                '      </body>',
            ])
    else:
        lines.append('      <geom name="snake_core" type="box" pos="0 0 0" size="0.30 0.16 0.08" mass="3"/>')
        for index in range(spec.n_gait_joints):
            x = (index - (spec.n_gait_joints - 1) / 2) * 0.18
            lines.extend([
                f'      <body name="segment_{index}" pos="{x:.3f} 0 -0.08">',
                f'        <joint name="gait_{index}" type="hinge" axis="0 1 0" damping="8"/>',
                f'        <geom name="segment_geom_{index}" type="capsule" fromto="-0.09 0 0 0.09 0 0" size="0.10" mass="0.35"/>',
                f'        <geom name="belly_{index}" type="sphere" pos="0 0 -0.14" size="0.075" mass="0.12" friction="0.01 0.01 0.01"/>',
                '      </body>',
            ])
    lines.extend(['    </body>', '  </worldbody>', '  <actuator>'])
    for joint in ROOT_JOINTS:
        kp = 900 if joint in {"root_x", "root_y", "root_z"} else 250
        lines.append(f'    <position name="act_{joint}" joint="{joint}" kp="{kp}" ctrlrange="-100 100"/>')
    for index in range(spec.n_gait_joints):
        gait_kp = 5000 if morph_id == "snake" else 500
        lines.append(f'    <position name="act_gait_{index}" joint="gait_{index}" kp="{gait_kp}" ctrlrange="-1 1"/>')
    lines.extend(['  </actuator>', '</mujoco>'])
    return "\n".join(lines) + "\n"


def write_g1_mjcf(morph_id: str, path: str | Path) -> None:
    Path(path).write_text(build_g1_mjcf(morph_id), encoding="utf-8")

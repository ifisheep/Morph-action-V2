"""Parameterised modular robot MJCF generator."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AssemblySpec:
    spine_segments: int = 3
    leg_pairs: int = 2
    module_length_m: float = 0.35
    module_radius_m: float = 0.08
    leg_length_m: float = 0.35
    camera_height_m: float = 0.45
    include_head: bool = True

    def __post_init__(self) -> None:
        if self.spine_segments < 1 or self.leg_pairs < 0:
            raise ValueError("assembly counts must be non-negative and non-zero")
        if min(self.module_length_m, self.module_radius_m, self.leg_length_m) <= 0:
            raise ValueError("module dimensions must be positive")


def build_mjcf(spec: AssemblySpec, *, model_name: str = "morphdream_robot") -> str:
    """Return a self-contained MJCF model using only standard MuJoCo elements."""
    lines = [
        f'<mujoco model="{model_name}">',
        '  <compiler angle="radian" coordinate="local"/>',
        '  <option gravity="0 0 -9.81"/>',
        '  <worldbody>',
        '    <body name="base" pos="0 0 0.5">',
        f'      <geom name="base_geom" type="box" size="{spec.module_length_m * spec.spine_segments / 2:.5f} {spec.module_radius_m:.5f} {spec.module_radius_m:.5f}" mass="1"/>',
    ]
    for index in range(spec.spine_segments):
        x = (index - (spec.spine_segments - 1) / 2) * spec.module_length_m
        lines.append(f'      <body name="spine_{index}" pos="{x:.5f} 0 0">')
        lines.append(f'        <joint name="spine_joint_{index}" type="hinge" axis="0 1 0"/>')
        lines.append(f'        <geom name="spine_geom_{index}" type="capsule" fromto="0 0 0 {spec.module_length_m:.5f} 0 0" size="{spec.module_radius_m:.5f}"/>')
        lines.append("      </body>")
    for pair in range(spec.leg_pairs):
        for side, y in (("left", spec.module_radius_m), ("right", -spec.module_radius_m)):
            x = (pair - (spec.leg_pairs - 1) / 2) * spec.module_length_m
            lines.extend([
                f'      <body name="leg_{side}_{pair}" pos="{x:.5f} {y:.5f} 0">',
                f'        <joint name="hip_{side}_{pair}" type="hinge" axis="0 1 0"/>',
                f'        <geom type="capsule" fromto="0 0 0 0 0 -{spec.leg_length_m:.5f}" size="{spec.module_radius_m * 0.7:.5f}"/>',
                "      </body>",
            ])
    if spec.include_head:
        lines.extend([
            f'      <body name="head" pos="0 0 {spec.camera_height_m:.5f}">',
            '        <joint name="neck_yaw" type="hinge" axis="0 0 1"/>',
            f'        <geom name="head_geom" type="sphere" size="{spec.module_radius_m * 1.2:.5f}"/>',
            '        <camera name="camera" pos="0 0 0" quat="1 0 0 0"/>',
            '      </body>',
        ])
    lines.extend(["    </body>", "  </worldbody>", "</mujoco>"])
    return "\n".join(lines) + "\n"


def write_mjcf(spec: AssemblySpec, path: str | Path, *, model_name: str = "morphdream_robot") -> None:
    Path(path).write_text(build_mjcf(spec, model_name=model_name), encoding="utf-8")

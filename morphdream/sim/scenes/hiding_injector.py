"""Geometry-based candidate hiding-location injector."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

import numpy as np

from .procedural_furniture import Furniture, ProceduralScene

HIDING_TYPES = ("under_bed", "under_sofa", "behind_obstacle", "high_shelf", "open_low_cubby")


@dataclass(frozen=True)
class HidingCandidate:
    hiding_type: str
    position_xyz: tuple[float, float, float]
    support_object_id: int | None
    clearance_height_m: float
    width_m: float
    visible_from_heights_m: tuple[float, ...]


def _candidate_for_support(kind: str, support: Furniture) -> HidingCandidate | None:
    center = np.asarray(support.center_xyz, dtype=float)
    size = np.asarray(support.size_xyz, dtype=float)
    if kind in {"under_bed", "under_sofa"}:
        if support.category != kind.removeprefix("under_"):
            return None
        clearance = max(0.05, float(center[2] - size[2] / 2))
        return HidingCandidate(kind, (float(center[0]), float(center[1]), clearance * 0.55), support.object_id, clearance, float(size[1] * 0.8), (0.25, 0.5, 1.0))
    if kind == "behind_obstacle":
        return HidingCandidate(kind, (float(center[0] + size[0] / 2 + 0.12), float(center[1]), 0.15), support.object_id, 0.3, float(size[1] * 0.6), (0.25, 0.5, 1.0))
    if kind == "high_shelf" and support.category in {"shelf", "cabinet"}:
        return HidingCandidate(kind, (float(center[0]), float(center[1]), float(center[2] + size[2] * 0.45)), support.object_id, 0.3, float(size[0] * 0.6), (1.2, 1.5, 1.8))
    if kind == "open_low_cubby" and support.category in {"shelf", "cabinet", "bookcase"}:
        return HidingCandidate(kind, (float(center[0]), float(center[1]), 0.35), support.object_id, 0.5, float(size[0] * 0.6), (0.25, 0.5, 1.0))
    return None


def find_candidates(scene: ProceduralScene) -> list[HidingCandidate]:
    candidates: list[HidingCandidate] = []
    for kind in HIDING_TYPES:
        for support in scene.objects:
            candidate = _candidate_for_support(kind, support)
            if candidate is not None:
                candidates.append(candidate)
    return candidates


def inject_target(scene: ProceduralScene, target: Furniture | None = None) -> tuple[ProceduralScene, HidingCandidate]:
    target = target or next((obj for obj in scene.objects if obj.object_id == scene.target_object_id), None)
    if target is None:
        raise ValueError("scene has no target object")
    candidates = find_candidates(scene)
    if not candidates:
        raise ValueError("scene has no geometrically valid hiding candidate")
    candidate = candidates[0]
    moved = [obj for obj in scene.objects if obj.object_id != target.object_id]
    moved.append(Furniture(target.object_id, target.category, candidate.position_xyz, target.size_xyz, target.color_rgb))
    return ProceduralScene(scene.scene_id, moved, target.object_id, candidate.hiding_type, dict(scene.metadata)), candidate


def main() -> None:
    parser = argparse.ArgumentParser(description="inject a target into a procedural scene")
    parser.add_argument("scene")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    scene, candidate = inject_target(ProceduralScene.load(args.scene))
    scene.save(args.output)
    print(json.dumps(asdict(candidate), indent=2))

"""Tier-0 imagination by ray casting through a read-only voxel snapshot."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from morphdream.core.types import ActionCandidate, MemorySnapshot, Pose, Resume, RobotState


def _target_center(snapshot: MemorySnapshot, region_id: str | None) -> np.ndarray:
    if region_id is not None:
        for obj in snapshot.objects:
            if str(obj.object_id) == region_id:
                return obj.center_xyz
    occupied = np.argwhere(snapshot.occupancy.values == 1)
    if occupied.size == 0:
        return snapshot.occupancy.origin_xyz + np.array([0.0, 0.0, 0.5])
    return snapshot.occupancy.origin_xyz + (occupied.mean(axis=0) + 0.5) * snapshot.occupancy.voxel_size_m


@dataclass
class Tier0Raycaster:
    step_m: float | None = None

    def visible_probability(self, snapshot: MemorySnapshot, viewpoint: Pose, target_xyz: np.ndarray) -> float:
        origin = viewpoint.position
        target = np.asarray(target_xyz, dtype=float)
        vector = target - origin
        distance = float(np.linalg.norm(vector))
        if distance <= 1e-9:
            return 1.0
        steps = max(1, int(np.ceil(distance / (self.step_m or snapshot.occupancy.voxel_size_m))))
        points = origin[None, :] + np.linspace(0.0, 1.0, steps + 1)[:, None] * vector[None, :]
        # Ignore the final target voxel and count unknown cells as uncertainty.
        states = [snapshot.occupancy.at(point) for point in points[1:-1]]
        if not states:
            return 1.0
        occupied = sum(state == 1 for state in states)
        unknown = sum(state == -1 for state in states)
        return float(np.clip(1.0 - occupied / len(states) - 0.25 * unknown / len(states), 0.0, 1.0))

    def score_candidate(self, snapshot: MemorySnapshot, candidate: ActionCandidate) -> float:
        viewpoint = candidate.viewpoint or Pose.identity()
        target = _target_center(snapshot, candidate.target_region_id)
        return self.visible_probability(snapshot, viewpoint, target)

    def score(self, mem: MemorySnapshot, cand: ActionCandidate, resumes: dict[str, Resume], state: RobotState):
        return self.score_candidate(mem, cand)

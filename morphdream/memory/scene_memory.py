"""Scene memory built exclusively from verified real-render observations."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from morphdream.core.types import (
    HypothesisSet,
    MemorySnapshot,
    ObjectRecord,
    Observation,
    SemanticGrid,
    VoxelGrid,
)


@dataclass
class SceneMemory:
    """A compact occupancy/semantic map with deterministic snapshotting.

    The CPU implementation uses a dense grid and a pinhole projection. A GPU
    backend can replace the projection routine without changing this contract.
    """

    voxel_size_m: float = 0.05
    bounds_min_xyz: tuple[float, float, float] = (-5.0, -5.0, 0.0)
    bounds_max_xyz: tuple[float, float, float] = (5.0, 5.0, 3.0)
    hypotheses: HypothesisSet = HypothesisSet({})

    def __post_init__(self) -> None:
        extent = np.asarray(self.bounds_max_xyz) - np.asarray(self.bounds_min_xyz)
        if np.any(extent <= 0) or self.voxel_size_m <= 0:
            raise ValueError("invalid memory bounds or voxel size")
        shape = np.ceil(extent / self.voxel_size_m).astype(int)
        self._occupancy = np.full(tuple(shape), -1, dtype=np.int8)
        self._semantics = np.zeros(tuple(shape), dtype=np.int32)
        self._class_names: dict[int, str] = {}
        self._objects: dict[int | str, ObjectRecord] = {}
        self._integrations = 0
        self._origin = np.asarray(self.bounds_min_xyz, dtype=float)

    @property
    def integration_count(self) -> int:
        return self._integrations

    def integrate(self, obs: Observation, verified: bool) -> None:
        if obs.source != "real_render" or not verified:
            raise ValueError("SceneMemory accepts only verified real_render observations")
        if obs.depth.shape != obs.seg.shape:
            raise ValueError("observation depth and segmentation shape mismatch")
        self._integrate_depth(obs)
        self._integrations += 1

    def _integrate_depth(self, obs: Observation) -> None:
        height, width = obs.depth.shape
        valid = np.isfinite(obs.depth) & (obs.depth > 0)
        if not np.any(valid):
            return
        ys, xs = np.nonzero(valid)
        depths = obs.depth[ys, xs]
        fx, fy = float(obs.K[0, 0]), float(obs.K[1, 1])
        cx, cy = float(obs.K[0, 2]), float(obs.K[1, 2])
        if fx <= 0 or fy <= 0:
            raise ValueError("camera intrinsics must have positive focal lengths")
        camera_points = np.stack(
            [(xs - cx) * depths / fx, (ys - cy) * depths / fy, depths], axis=1
        )
        world_points = (obs.T_world_cam[:3, :3] @ camera_points.T).T + obs.T_world_cam[:3, 3]
        indices = np.floor((world_points - self._origin) / self.voxel_size_m).astype(int)
        in_bounds = np.all((indices >= 0) & (indices < np.asarray(self._occupancy.shape)), axis=1)
        indices = indices[in_bounds]
        labels = obs.seg[ys, xs][in_bounds]
        for (ix, iy, iz), label in zip(indices, labels):
            self._occupancy[ix, iy, iz] = 1
            self._semantics[ix, iy, iz] = int(label)
            if int(label) in obs.seg_classes:
                self._class_names[int(label)] = obs.seg_classes[int(label)]

    def add_object(self, record: ObjectRecord) -> None:
        self._objects[record.object_id] = record

    def snapshot(self) -> MemorySnapshot:
        occupancy = VoxelGrid(self._occupancy.copy(), self._origin.copy(), self.voxel_size_m)
        semantics = SemanticGrid(self._semantics.copy(), dict(self._class_names))
        return MemorySnapshot(occupancy, semantics, self.hypotheses, tuple(self._objects.values()))

    def reset(self) -> None:
        self._occupancy.fill(-1)
        self._semantics.fill(0)
        self._class_names.clear()
        self._objects.clear()
        self._integrations = 0

    def occupied_fraction(self) -> float:
        return float(np.mean(self._occupancy == 1))


def snapshot_from_arrays(
    occupancy: np.ndarray,
    semantics: np.ndarray | None = None,
    *,
    origin_xyz: tuple[float, float, float] = (0.0, 0.0, 0.0),
    voxel_size_m: float = 0.05,
    hypotheses: HypothesisSet | None = None,
) -> MemorySnapshot:
    """Build a snapshot for tests and offline evaluators."""
    occ = VoxelGrid(occupancy, np.asarray(origin_xyz), voxel_size_m)
    sem = SemanticGrid(np.zeros_like(occ.values) if semantics is None else semantics)
    return MemorySnapshot(occ, sem, hypotheses or HypothesisSet({}))

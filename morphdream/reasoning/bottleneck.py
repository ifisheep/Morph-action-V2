"""Bottleneck diagnosis from geometry and morphology resumes."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np

from morphdream.core.types import Bottleneck, MemorySnapshot, Pose, RegionRef, Resume


def _region_for_object(snapshot: MemorySnapshot, object_id: int | str) -> RegionRef:
    for obj in snapshot.objects:
        if obj.object_id == object_id:
            return RegionRef(str(object_id), obj.center_xyz, obj.size_xyz)
    raise KeyError(f"unknown object id {object_id}")


def sample_remedy_viewpoints(region: RegionRef, resume: Resume, count: int = 8) -> list[Pose]:
    center = region.center_xyz
    radius = max(float(np.max(region.size_xyz)) * 2, 0.6)
    viewpoints: list[Pose] = []
    for angle in np.linspace(0, 2 * np.pi, max(1, count), endpoint=False):
        position = center + np.array([radius * np.cos(angle), radius * np.sin(angle), np.mean(resume.camera_height_range_m)])
        viewpoints.append(Pose(position))
    return viewpoints


def diagnose_bottlenecks(
    snapshot: MemorySnapshot,
    object_id: int | str,
    resumes: Mapping[str, Resume],
    *,
    observed_fraction: float = 0.0,
    image_width_px: int = 128,
) -> list[Bottleneck]:
    region = _region_for_object(snapshot, object_id)
    size = region.size_xyz
    bottlenecks: list[Bottleneck] = []
    if observed_fraction < 0.2:
        bottlenecks.append(Bottleneck("occlusion", region, details={"observed_fraction": observed_fraction}))
    if float(np.min(size)) * image_width_px < 6:
        bottlenecks.append(Bottleneck("scale", region, details={"projected_min_px": float(np.min(size) * image_width_px)}))
    if not bottlenecks:
        bottlenecks.append(Bottleneck("fov", region, details={"reason": "target is outside current view"}))
    for index, item in enumerate(bottlenecks):
        reachable = {}
        for morph_id, resume in resumes.items():
            reachable[morph_id] = bool(resume.reachable_camera_poses.size)
        viewpoints = sample_remedy_viewpoints(region, next(iter(resumes.values())), 8) if resumes else []
        bottlenecks[index] = Bottleneck(item.kind, region, tuple(viewpoints), reachable, item.details)
    return bottlenecks


def classify_visibility(
    target_xyz: Sequence[float], camera_xyz: Sequence[float], image_radius_px: float, *, min_radius_px: float = 4.0
) -> str:
    distance = float(np.linalg.norm(np.asarray(target_xyz) - np.asarray(camera_xyz)))
    if image_radius_px < min_radius_px:
        return "scale"
    if distance < 0.05:
        return "quality"
    return "occlusion"

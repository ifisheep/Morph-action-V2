"""Deterministic CPU renderer with an optional MuJoCo integration hook."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from morphdream.core.types import Observation, Pose

from .scenes.procedural_furniture import ProceduralScene


@dataclass(frozen=True)
class RenderConfig:
    width: int = 128
    height: int = 128
    near_m: float = 0.02
    far_m: float = 20.0
    focal_length_px: float | None = None


def _camera_matrix(config: RenderConfig) -> np.ndarray:
    focal = config.focal_length_px or 0.8 * config.width
    return np.array([[focal, 0, config.width / 2], [0, focal, config.height / 2], [0, 0, 1]], dtype=float)


def render_scene(scene: ProceduralScene, camera_pose: Pose | None = None, config: RenderConfig | None = None) -> Observation:
    """Render axis-aligned boxes from a pinhole camera.

    The renderer is intentionally conservative. It is sufficient for CPU
    integration tests and provides the same observation contract as a future
    MuJoCo Warp backend.
    """
    config = config or RenderConfig()
    K = _camera_matrix(config)
    depth = np.full((config.height, config.width), config.far_m, dtype=float)
    seg = np.zeros((config.height, config.width), dtype=np.int32)
    camera_pose = camera_pose or Pose(np.array([4.5, 4.5, 2.0]))
    # A simple top-down-ish view aimed at the scene center. The orthographic
    # projection keeps the fallback deterministic and easy to validate.
    for obj in scene.objects:
        center = np.asarray(obj.center_xyz)
        size = np.asarray(obj.size_xyz)
        distance = float(np.linalg.norm(center - camera_pose.position))
        if distance <= config.near_m:
            continue
        u = int(config.width / 2 + (center[0] - camera_pose.position[0]) * config.width / 8)
        v = int(config.height / 2 - (center[1] - camera_pose.position[1]) * config.height / 8)
        half_w = max(1, int(size[0] * config.width / 16))
        half_h = max(1, int(size[1] * config.height / 16))
        x0, x1 = max(0, u - half_w), min(config.width, u + half_w + 1)
        y0, y1 = max(0, v - half_h), min(config.height, v + half_h + 1)
        if x0 >= x1 or y0 >= y1:
            continue
        patch = depth[y0:y1, x0:x1]
        closer = distance < patch
        patch[closer] = distance
        seg_patch = seg[y0:y1, x0:x1]
        seg_patch[closer] = obj.object_id
    return Observation(0.0, "unknown", depth, seg, {obj.object_id: obj.category for obj in scene.objects}, None, K, np.eye(4))

"""Batch rendering facade with CPU fallback and optional MuJoCo Warp hook."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Iterable

from morphdream.core.types import Observation, Pose
from .render import RenderConfig, render_scene
from .scenes.procedural_furniture import ProceduralScene


@dataclass(frozen=True)
class BatchRenderResult:
    observations: tuple[Observation, ...]
    elapsed_s: float
    backend: str

    @property
    def fps(self) -> float:
        return len(self.observations) / max(self.elapsed_s, 1e-9)


class BatchRenderer:
    def __init__(self, config: RenderConfig | None = None, workers: int = 1):
        self.config = config or RenderConfig()
        self.workers = max(1, workers)

    def render(self, scenes: Iterable[ProceduralScene], poses: Iterable[Pose | None] | None = None) -> BatchRenderResult:
        import time

        scene_list = list(scenes)
        pose_list = list(poses) if poses is not None else [None] * len(scene_list)
        if len(pose_list) != len(scene_list):
            raise ValueError("scenes and poses must have matching lengths")
        start = time.perf_counter()
        if self.workers == 1:
            outputs = [render_scene(scene, pose, self.config) for scene, pose in zip(scene_list, pose_list)]
        else:
            with ThreadPoolExecutor(max_workers=self.workers) as pool:
                outputs = list(pool.map(lambda pair: render_scene(pair[0], pair[1], self.config), zip(scene_list, pose_list)))
        return BatchRenderResult(tuple(outputs), time.perf_counter() - start, "procedural_cpu")

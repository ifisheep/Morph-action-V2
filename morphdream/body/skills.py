"""L1 skills shared by simulation and the future hardware backend."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from morphdream.core.types import Pose2D, SkillResult

from .backends.sim import SimulationBackend
from .gaze import GazeController


@dataclass(frozen=True)
class BodyConfig:
    default_speed_mps: float = 0.25
    transition_overhead_s: float = 0.5


class SimBody:
    def __init__(self, morph_id: str = "quadruped", config: BodyConfig | None = None, backend: SimulationBackend | None = None):
        self.config = config or BodyConfig()
        self.backend = backend or SimulationBackend(morph_id)
        self.gaze = GazeController()

    @property
    def morph_id(self) -> str:
        return self.backend.morph_id

    @property
    def state(self):
        return self.backend.state

    def transition_to(self, morph_id: str) -> SkillResult:
        result = self.backend.transition_to(morph_id)
        if result.success and result.duration_s > 0:
            return SkillResult(True, result.duration_s + self.config.transition_overhead_s, result.fell, result.observations, result.details)
        return result

    def move_to(self, pose2d: Pose2D, speed: float | None = None) -> SkillResult:
        return self.backend.move_to(pose2d, speed or self.config.default_speed_mps)

    def look_at(self, target_xyz: np.ndarray, stabilize: bool = True) -> SkillResult:
        camera = self.state.pose.position + np.array([0.0, 0.0, 0.45])
        self.gaze.look_at(target_xyz, camera, stabilize=stabilize, body_velocity=np.array([self.state.velocity_mps, 0.0, 0.0]))
        return self.backend.look_at(target_xyz, stabilize)

    def scan(self, yaw_range: tuple[float, float], pitch_range: tuple[float, float]) -> SkillResult:
        return self.backend.scan(yaw_range, pitch_range)

    def pause(self, seconds: float) -> SkillResult:
        return self.backend.pause(seconds)

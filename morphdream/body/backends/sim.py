from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from morphdream.core.types import Pose, Pose2D, RobotState, SkillResult


@dataclass
class SimulationBackend:
    morph_id: str = "quadruped"
    state: RobotState | None = None

    def __post_init__(self) -> None:
        self.state = self.state or RobotState(self.morph_id)

    def transition_to(self, morph_id: str) -> SkillResult:
        if morph_id == self.morph_id:
            return SkillResult(True, 0.0, False)
        duration = 1.5 + 0.15 * abs(len(morph_id) - len(self.morph_id))
        self.morph_id = morph_id
        self.state = RobotState(morph_id, self.state.pose)
        return SkillResult(True, duration, False)

    def move_to(self, pose2d: Pose2D, speed: float) -> SkillResult:
        if speed <= 0:
            return SkillResult(False, 0.0, False, details={"error": "speed must be positive"})
        current = self.state.pose.position
        distance = float(np.hypot(pose2d.x - current[0], pose2d.y - current[1]))
        duration = distance / speed
        pose = Pose(np.array([pose2d.x, pose2d.y, current[2]]), self.state.pose.quaternion)
        self.state = RobotState(self.morph_id, pose, speed)
        return SkillResult(True, duration, False)

    def look_at(self, target_xyz: np.ndarray, stabilize: bool = True) -> SkillResult:
        return SkillResult(True, 0.15 if stabilize else 0.10, False)

    def scan(self, yaw_range: tuple[float, float], pitch_range: tuple[float, float]) -> SkillResult:
        duration = max(0.1, abs(yaw_range[1] - yaw_range[0]) + abs(pitch_range[1] - pitch_range[0]))
        return SkillResult(True, duration, False)

    def pause(self, seconds: float) -> SkillResult:
        return SkillResult(seconds >= 0, max(0.0, seconds), False)

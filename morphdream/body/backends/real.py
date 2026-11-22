"""Hardware abstraction placeholder for future experiments."""

from __future__ import annotations

from morphdream.core.types import Pose2D, SkillResult


class RealRobotBackend:
    def _unavailable(self) -> SkillResult:
        return SkillResult(False, 0.0, False, details={"error": "real hardware backend is not configured"})

    def transition_to(self, morph_id: str) -> SkillResult:
        return self._unavailable()

    def move_to(self, pose2d: Pose2D, speed: float) -> SkillResult:
        return self._unavailable()

    def look_at(self, target_xyz, stabilize: bool = True) -> SkillResult:
        return self._unavailable()

    def scan(self, yaw_range, pitch_range) -> SkillResult:
        return self._unavailable()

    def pause(self, seconds: float) -> SkillResult:
        return self._unavailable()

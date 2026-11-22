"""Camera gaze and motion-prediction stabilisation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class GazeController:
    max_pitch_rad: float = 1.2
    max_yaw_rad: float = 2.8
    feedforward_gain: float = 0.65
    pitch_rad: float = 0.0
    yaw_rad: float = 0.0

    def look_at(self, target_xyz: np.ndarray, camera_xyz: np.ndarray, *, stabilize: bool = True, body_velocity: np.ndarray | None = None) -> tuple[float, float]:
        target = np.asarray(target_xyz, dtype=float) - np.asarray(camera_xyz, dtype=float)
        yaw = float(np.arctan2(target[1], target[0]))
        pitch = float(np.arctan2(target[2], max(np.hypot(target[0], target[1]), 1e-6)))
        if stabilize and body_velocity is not None:
            velocity = np.asarray(body_velocity, dtype=float).reshape(-1)
            yaw -= self.feedforward_gain * float(velocity[1]) if velocity.size > 1 else 0.0
            pitch += self.feedforward_gain * float(velocity[2]) if velocity.size > 2 else 0.0
        self.yaw_rad = float(np.clip(yaw, -self.max_yaw_rad, self.max_yaw_rad))
        self.pitch_rad = float(np.clip(pitch, -self.max_pitch_rad, self.max_pitch_rad))
        return self.yaw_rad, self.pitch_rad

    def predicted_jitter(self, speed_mps: float, *, stabilize: bool = True) -> float:
        base = 0.08 * max(speed_mps, 0.0)
        return base * (0.45 if stabilize else 1.0)

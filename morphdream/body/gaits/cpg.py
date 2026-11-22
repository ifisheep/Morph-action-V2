"""Lightweight central-pattern-generator gait primitives."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CPGConfig:
    frequency_hz: float = 1.5
    amplitude: float = 0.25
    phase_offsets: tuple[float, ...] = (0.0, 3.141592653589793)
    duty_factor: float = 0.5

    def __post_init__(self) -> None:
        if self.frequency_hz <= 0 or self.amplitude < 0 or not 0 < self.duty_factor <= 1:
            raise ValueError("invalid CPG parameters")


@dataclass(frozen=True)
class CPGState:
    time_s: float
    phases: np.ndarray
    outputs: np.ndarray


def central_pattern_generator(time_s: float, config: CPGConfig, n_oscillators: int | None = None) -> CPGState:
    phases = np.asarray(config.phase_offsets if n_oscillators is None else tuple(
        2 * np.pi * i / n_oscillators for i in range(n_oscillators)
    )) + 2 * np.pi * config.frequency_hz * time_s
    outputs = config.amplitude * np.sin(phases)
    return CPGState(float(time_s), np.mod(phases, 2 * np.pi), outputs)


def gait_parameters(morph_id: str) -> CPGConfig:
    return {
        "quadruped": CPGConfig(1.8, 0.22, (0, np.pi, np.pi, 0)),
        "snake": CPGConfig(1.2, 0.30, tuple(i * np.pi / 2 for i in range(8))),
        "centaur": CPGConfig(1.3, 0.18, (0, np.pi, np.pi, 0)),
        "hexapod": CPGConfig(1.6, 0.20, (0, np.pi, 0, np.pi, 0, np.pi)),
        "periscope": CPGConfig(1.0, 0.12, (0, np.pi)),
    }.get(morph_id, CPGConfig())

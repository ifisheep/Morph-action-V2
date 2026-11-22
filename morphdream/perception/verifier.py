"""Verifier boundary for true rendered observations and open-vocabulary detectors."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from morphdream.core.types import Observation


@dataclass(frozen=True)
class VerificationResult:
    accepted: bool
    confidence: float
    visible_fraction: float
    details: dict[str, float]


class DetectionVerifier:
    def __init__(self, min_visible_fraction: float = 0.01):
        self.min_visible_fraction = min_visible_fraction

    def verify(self, obs: Observation, target_class: str) -> VerificationResult:
        if obs.source != "real_render":
            raise ValueError("verifier accepts only real_render observations")
        matching = [instance for instance, name in obs.seg_classes.items() if name == target_class]
        visible = float(np.mean(np.isin(obs.seg, matching))) if matching else 0.0
        confidence = min(1.0, visible / max(self.min_visible_fraction, 1e-9))
        return VerificationResult(visible >= self.min_visible_fraction, confidence, visible, {"instances": float(len(matching))})

    def detect(self, obs: Observation, vocabulary: list[str]) -> dict[str, VerificationResult]:
        return {name: self.verify(obs, name) for name in vocabulary}

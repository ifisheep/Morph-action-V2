"""Configurable depth and segmentation noise model."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from morphdream.core.types import Observation


@dataclass(frozen=True)
class NoiseConfig:
    depth_sigma_m: float = 0.01
    segmentation_drop_prob: float = 0.02
    segmentation_false_positive_prob: float = 0.005
    seed: int = 0

    def __post_init__(self) -> None:
        if self.depth_sigma_m < 0 or not 0 <= self.segmentation_drop_prob <= 1 or not 0 <= self.segmentation_false_positive_prob <= 1:
            raise ValueError("invalid noise probabilities")


def apply_noise(obs: Observation, config: NoiseConfig | None = None, *, seed: int | None = None) -> Observation:
    config = config or NoiseConfig()
    rng = np.random.default_rng(config.seed if seed is None else seed)
    depth = np.maximum(0.0, obs.depth + rng.normal(0.0, config.depth_sigma_m, obs.depth.shape))
    seg = obs.seg.copy()
    drop = rng.random(seg.shape) < config.segmentation_drop_prob
    seg[drop] = 0
    false_positive = (seg == 0) & (rng.random(seg.shape) < config.segmentation_false_positive_prob)
    if obs.seg_classes:
        seg[false_positive] = int(sorted(obs.seg_classes)[0])
    return Observation(obs.t, obs.morph_id, depth, seg, dict(obs.seg_classes), None if obs.rgb is None else obs.rgb.copy(), obs.K.copy(), obs.T_world_cam.copy())

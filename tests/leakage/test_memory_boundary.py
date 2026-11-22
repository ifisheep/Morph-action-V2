"""Tests for the dream/wake observation boundary."""

from __future__ import annotations

import numpy as np
import pytest

from morphdream.core.types import Observation
from morphdream.memory.scene_memory import SceneMemory


def _observation() -> Observation:
    return Observation(
        t=0.0,
        morph_id="quadruped",
        depth=np.ones((4, 4), dtype=float),
        seg=np.zeros((4, 4), dtype=np.int32),
        seg_classes={},
        rgb=None,
        K=np.eye(3),
        T_world_cam=np.eye(4),
    )


def test_only_verified_real_render_updates_memory() -> None:
    memory = SceneMemory()
    memory.integrate(_observation(), verified=True)
    before = memory.snapshot().content_hash

    with pytest.raises((ValueError, PermissionError)):
        memory.integrate(_observation(), verified=False)
    assert memory.snapshot().content_hash == before


def test_imagined_observation_is_rejected() -> None:
    memory = SceneMemory()
    imagined = _observation()
    # Observation validates the normal constructor value. Mutating the source
    # here models an imagined record that bypassed the regular renderer API.
    imagined.source = "imagined"  # type: ignore[assignment]
    with pytest.raises((ValueError, PermissionError)):
        memory.integrate(imagined, verified=True)

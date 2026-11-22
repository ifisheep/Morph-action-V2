"""A100-only one-second smoke test for the G1 MuJoCo models."""

from __future__ import annotations

import pytest

pytest.importorskip("mujoco")

from morphdream.g1.criteria import FallCriteria, Scenario
from morphdream.g1.runner import G1PhysicsRunner


@pytest.mark.gpu
@pytest.mark.integration
def test_g1_models_walk_for_one_second_without_falling() -> None:
    criteria = FallCriteria(0.7853981633974483, 0.12, 0.25)
    scenario = Scenario("g1-mini", 20261122, {"kind": "flat"}, {"x_m": 0.0, "y_m": 0.0, "yaw_rad": 0.0}, 1.0, 1.0)
    for morphology in ("quadruped", "snake", "centaur"):
        runner = G1PhysicsRunner(morphology, criteria)
        trace = runner.run_episode(scenario)
        assert not trace.fell
        assert trace.duration_s >= 1.0

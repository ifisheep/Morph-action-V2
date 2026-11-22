"""Small end-to-end CPU smoke test for the decision loop."""

from __future__ import annotations

import numpy as np

from morphdream.core.types import ObjectRecord
from morphdream.decision.loop import RunConfig, run_episodes
from morphdream.memory.scene_memory import SceneMemory
from morphdream.resume.measure import MeasureConfig, measure_resume


def test_cpu_smoke_runner_writes_reproducible_artifacts(tmp_path) -> None:
    memory = SceneMemory()
    memory.add_object(
        ObjectRecord("target", "apple", np.array([1.0, 0.0, 0.4]), np.array([0.1, 0.1, 0.1]))
    )
    snapshot = memory.snapshot()
    resumes = {
        name: measure_resume(name, MeasureConfig(trials=2, duration_s=1.0, seed=7))
        for name in ("quadruped", "snake", "centaur")
    }
    config = RunConfig(episodes=2, max_steps=3, output_dir=str(tmp_path), seed=11)
    results = run_episodes(lambda _: snapshot, "target", resumes, config)

    assert len(results) == 2
    assert all(result.steps <= 3 for result in results)
    assert (tmp_path / "episodes.jsonl").exists()
    assert (tmp_path / "summary.json").exists()

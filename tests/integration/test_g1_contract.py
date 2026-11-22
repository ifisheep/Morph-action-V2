"""Fast contract checks for the frozen G1 acceptance inputs."""

from __future__ import annotations

from pathlib import Path

from morphdream.g1.criteria import load_frozen_config, load_scenarios


ROOT = Path(__file__).resolve().parents[2]


def test_g1_inputs_are_frozen_and_complete() -> None:
    config, config_hash = load_frozen_config(ROOT / "configs/g1.yaml")
    scenarios = load_scenarios(ROOT / config["scene_manifest"], expected_count=50)
    assert config_hash
    assert config["episode_duration_s"] == 60.0
    assert tuple(config["morphologies"]) == ("quadruped", "snake", "centaur")
    assert len(scenarios) == 50
    assert len({scenario.scene_id for scenario in scenarios}) == 50
    assert config["transitions"]["trials_per_edge"] == 100

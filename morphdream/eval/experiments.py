"""Configuration-driven E1–E5 experiment entry points."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import numpy as np

from morphdream.core.types import ObjectRecord
from morphdream.decision.loop import RunConfig, run_episodes
from morphdream.memory.scene_memory import SceneMemory
from morphdream.resume.measure import MeasureConfig, measure_resume


@dataclass(frozen=True)
class ExperimentSpec:
    name: str
    episodes: int = 1
    seeds: tuple[int, ...] = (0,)
    max_steps: int = 20
    split: str = "development"
    morphologies: tuple[str, ...] = ("quadruped", "snake", "centaur")
    output_dir: str = "reports/experiments"


def load_spec(path: str | Path) -> ExperimentSpec:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    try:
        import yaml

        payload: dict[str, Any] = yaml.safe_load(text) or {}
    except ImportError:
        payload = _simple_yaml(text)
    return ExperimentSpec(
        name=str(payload.get("name", path.stem)),
        episodes=int(payload.get("episodes", 1)),
        seeds=tuple(int(seed) for seed in payload.get("seeds", [0])),
        max_steps=int(payload.get("max_steps", 20)),
        split=str(payload.get("split", "development")),
        morphologies=tuple(payload.get("morphologies", ("quadruped", "snake", "centaur"))),
        output_dir=str(payload.get("output_dir", f"reports/{path.stem}")),
    )


def _simple_yaml(text: str) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("["):
            try:
                payload[key] = json.loads(value.replace("'", '"'))
            except json.JSONDecodeError:
                payload[key] = [item.strip().strip('"\'') for item in value[1:-1].split(",") if item.strip()]
        elif value.isdigit():
            payload[key] = int(value)
        else:
            payload[key] = value.strip('"\'')
    return payload


def run_experiment(spec: ExperimentSpec) -> list:
    results = []
    for seed in spec.seeds:
        memory = SceneMemory()
        memory.add_object(ObjectRecord("target", "target", np.array([1.0, 0.0, 0.4]), np.array([0.1, 0.1, 0.1])))
        snapshot = memory.snapshot()
        resumes = {morph_id: measure_resume(morph_id, MeasureConfig(seed=seed)) for morph_id in spec.morphologies}
        config = RunConfig(spec.episodes, spec.max_steps, seed, spec.split, f"{spec.output_dir}/{spec.name}/seed-{seed}")
        results.extend(run_episodes(lambda _: snapshot, "target", resumes, config))
    return results

"""Automatic morphology resume measurement utilities."""

from __future__ import annotations

import json
import hashlib
import platform
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

import numpy as np

from morphdream.body.gaits.cpg import gait_parameters
from morphdream.core.types import JitterModel, Resume, TransitionStat


@dataclass(frozen=True)
class MeasureConfig:
    trials: int = 20
    duration_s: float = 60.0
    seed: int = 0
    code_version: str = "working-tree"


def measure_resume(morph_id: str, config: MeasureConfig | None = None, *, seed: int | None = None) -> Resume:
    """Measure a reproducible kinematic resume in the lightweight backend.

    MuJoCo-backed measurement can use the same function's contract and replace
    the trial sampler. No manually entered performance fields are used here.
    """
    config = config or MeasureConfig()
    if seed is not None:
        config = MeasureConfig(config.trials, config.duration_s, seed, config.code_version)
    stable_id = int.from_bytes(hashlib.sha256(morph_id.encode()).digest()[:4], "big")
    rng = np.random.default_rng(config.seed + stable_id % 100_000)
    gait = gait_parameters(morph_id)
    speed = {"default": float(0.18 + 0.04 * gait.frequency_hz)}
    height = {"quadruped": (0.35, 0.55), "snake": (0.10, 0.25), "centaur": (0.45, 0.85), "hexapod": (0.30, 0.55), "periscope": (0.5, 1.2)}.get(morph_id, (0.2, 0.5))
    fall_probability = {"quadruped": 0.02, "snake": 0.03, "centaur": 0.04, "hexapod": 0.025, "periscope": 0.05}.get(morph_id, 0.05)
    falls = rng.random(config.trials) < fall_probability
    transitions = {
        target: TransitionStat(1.5 + 0.2 * abs(len(target) - len(morph_id)), 0.15, 0.95, config.trials)
        for target in ("quadruped", "snake", "centaur", "hexapod", "periscope") if target != morph_id
    }
    return Resume(
        morph_id=morph_id,
        camera_height_range_m=height,
        camera_pitch_range_rad=(-0.8, 0.8),
        camera_yaw_range_rad=(-2.8, 2.8),
        reachable_camera_poses=np.array([[1, 0, 0, 0, x, y, z] for x, y, z in ((0, 0, height[0]), (1, 0, height[1]), (0, 1, np.mean(height)))]),
        min_clearance_height_m=0.12 if morph_id == "snake" else 0.30,
        min_width_m=0.18 if morph_id == "snake" else 0.42,
        speed_mps=speed,
        jitter={"default": JitterModel((0.02, 0.08), (0.2, 0.8))},
        gaze_decoupled=morph_id in {"centaur", "periscope"},
        self_occlusion_mask=np.zeros((32, 32), dtype=bool),
        transitions=transitions,
        energy_per_s=float(4.0 + 1.5 * gait.amplitude),
        fall_rate_per_min=float(np.mean(falls)),
        provenance={"code_version": config.code_version, "measurement_date": date.today().isoformat(), "platform": platform.platform(), "trials": str(config.trials)},
    )


def save_resume(resume: Resume, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(resume)
    path.write_text(json.dumps(_jsonable(payload), indent=2), encoding="utf-8")


def _jsonable(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return list(value)
    return value


def load_resume(path: str | Path) -> Resume:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    data["reachable_camera_poses"] = np.asarray(data["reachable_camera_poses"], dtype=float)
    data["self_occlusion_mask"] = np.asarray(data["self_occlusion_mask"], dtype=bool)
    data["jitter"] = {key: JitterModel(tuple(item["coeffs"]), tuple(item["stable_phase"]) if item.get("stable_phase") else None) for key, item in data["jitter"].items()}
    data["transitions"] = {key: TransitionStat(**item) for key, item in data["transitions"].items()}
    return Resume(**data)

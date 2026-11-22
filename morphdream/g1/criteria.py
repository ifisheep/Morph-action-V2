"""Frozen G1 evaluation criteria and metric aggregation.

This module contains the measurement contract only. It deliberately does not
change the robot model or the shared core interfaces.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np


@dataclass(frozen=True)
class FallCriteria:
    max_body_tilt_rad: float
    min_body_height_m: float
    non_foot_contact_duration_s: float
    terminal_if_simulation_nan: bool = True

    def evaluate(self, sample: "BodySample", *, non_foot_contact_duration_s: float = 0.0) -> "FallEvent | None":
        if self.terminal_if_simulation_nan and not sample.is_finite:
            return FallEvent(sample.time_s, "simulation_nan")
        if abs(sample.roll_rad) > self.max_body_tilt_rad or abs(sample.pitch_rad) > self.max_body_tilt_rad:
            return FallEvent(sample.time_s, "body_tilt")
        if sample.height_m < self.min_body_height_m:
            return FallEvent(sample.time_s, "body_height")
        if non_foot_contact_duration_s >= self.non_foot_contact_duration_s:
            return FallEvent(sample.time_s, "non_foot_contact")
        return None


@dataclass(frozen=True)
class BodySample:
    time_s: float
    height_m: float
    roll_rad: float
    pitch_rad: float
    contact_names: tuple[str, ...] = ()

    @property
    def is_finite(self) -> bool:
        return bool(np.isfinite([self.time_s, self.height_m, self.roll_rad, self.pitch_rad]).all())


@dataclass(frozen=True)
class FallEvent:
    time_s: float
    reason: str


@dataclass(frozen=True)
class Scenario:
    scene_id: str
    seed: int
    terrain: Mapping[str, float | str]
    start_pose: Mapping[str, float]
    distance_m: float
    duration_s: float


@dataclass(frozen=True)
class G1Metrics:
    morphology_trials: Mapping[str, int]
    morphology_falls: Mapping[str, int]
    transition_trials: Mapping[str, int]
    transition_successes: Mapping[str, int]
    lock_max_abs_angle_rad: float
    jitter_off_rad: float
    jitter_on_rad: float
    scenario_ids: tuple[str, ...]
    seed: int
    config_sha256: str
    commit: str
    details: Mapping[str, Any] = field(default_factory=dict)

    @property
    def fall_rates(self) -> dict[str, float]:
        return {
            morph_id: self.morphology_falls.get(morph_id, 0) / max(self.morphology_trials.get(morph_id, 0), 1)
            for morph_id in self.morphology_trials
        }

    @property
    def transition_success_rates(self) -> dict[str, float]:
        return {
            edge: self.transition_successes.get(edge, 0) / max(self.transition_trials.get(edge, 0), 1)
            for edge in self.transition_trials
        }

    @property
    def stabilization_ratio(self) -> float:
        return self.jitter_on_rad / max(self.jitter_off_rad, 1e-12)

    def as_json(self) -> dict[str, Any]:
        return {
            "morphology_trials": dict(self.morphology_trials),
            "morphology_falls": dict(self.morphology_falls),
            "fall_rates": self.fall_rates,
            "transition_trials": dict(self.transition_trials),
            "transition_successes": dict(self.transition_successes),
            "transition_success_rates": self.transition_success_rates,
            "lock_max_abs_angle_rad": self.lock_max_abs_angle_rad,
            "jitter_off_rad": self.jitter_off_rad,
            "jitter_on_rad": self.jitter_on_rad,
            "stabilization_ratio": self.stabilization_ratio,
            "scenario_ids": list(self.scenario_ids),
            "seed": self.seed,
            "config_sha256": self.config_sha256,
            "commit": self.commit,
            "details": dict(self.details),
        }


def frozen_sha256(path: str | Path) -> str:
    return sha256(Path(path).read_bytes()).hexdigest()


def _parse_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml

        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("G1 config must contain a mapping")
        return payload
    except ImportError as exc:
        raise RuntimeError("G1 requires PyYAML in the independent evaluation environment") from exc


def load_frozen_config(path: str | Path) -> tuple[dict[str, Any], str]:
    path = Path(path)
    payload = _parse_yaml(path)
    if payload.get("frozen") is not True:
        raise ValueError("G1 criteria must be marked frozen before evaluation")
    if int(payload.get("scene_count", 0)) != 50:
        raise ValueError("G1 requires exactly 50 evaluation scenes")
    if float(payload.get("episode_duration_s", 0)) != 60.0:
        raise ValueError("G1 episodes must run for 60 seconds")
    return payload, frozen_sha256(path)


def load_scenarios(path: str | Path, *, expected_count: int = 50) -> tuple[Scenario, ...]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("frozen") is not True:
        raise ValueError("G1 scenario manifest must be frozen")
    raw = payload.get("scenarios", [])
    if len(raw) != expected_count:
        raise ValueError(f"G1 scenario manifest must contain {expected_count} scenarios")
    scenarios = tuple(Scenario(**item) for item in raw)
    ids = [scenario.scene_id for scenario in scenarios]
    if len(set(ids)) != len(ids):
        raise ValueError("G1 scenario ids must be unique")
    return scenarios


def aggregate_g1(
    morphology_trials: Mapping[str, int],
    morphology_falls: Mapping[str, int],
    transition_trials: Mapping[str, int],
    transition_successes: Mapping[str, int],
    *,
    lock_max_abs_angle_rad: float,
    jitter_off_rad: float,
    jitter_on_rad: float,
    scenarios: Iterable[Scenario],
    seed: int,
    config_sha256: str,
    commit: str,
    details: Mapping[str, Any] | None = None,
) -> G1Metrics:
    return G1Metrics(
        dict(morphology_trials),
        dict(morphology_falls),
        dict(transition_trials),
        dict(transition_successes),
        float(lock_max_abs_angle_rad),
        float(jitter_off_rad),
        float(jitter_on_rad),
        tuple(s.scene_id for s in scenarios),
        seed,
        config_sha256,
        commit,
        dict(details or {}),
    )

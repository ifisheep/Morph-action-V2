"""Paper-facing metrics and paired bootstrap confidence intervals."""

from __future__ import annotations

import numpy as np


def aggregate_metrics(records: list[dict]) -> dict[str, float]:
    if not records:
        return {"success_rate": 0.0, "median_steps": 0.0, "median_duration_s": 0.0, "median_thinking_time_s": 0.0, "median_simulation_time_s": 0.0}
    success = np.asarray([bool(item.get("success", False)) for item in records])
    return {
        "success_rate": float(np.mean(success)),
        "median_steps": float(np.median([item.get("step", 0) + 1 for item in records])),
        "median_duration_s": float(np.median([item.get("duration_s", item.get("simulation_time_s", 0.0)) for item in records])),
        "median_thinking_time_s": float(np.median([item.get("thinking_time_s", 0.0) for item in records])),
        "median_simulation_time_s": float(np.median([item.get("simulation_time_s", 0.0) for item in records])),
    }


def paired_bootstrap_ci(differences, *, n_boot: int = 2000, confidence: float = 0.95, seed: int = 0) -> tuple[float, float]:
    values = np.asarray(differences, dtype=float)
    if values.size == 0:
        return (0.0, 0.0)
    rng = np.random.default_rng(seed)
    samples = rng.choice(values, size=(n_boot, values.size), replace=True).mean(axis=1)
    alpha = (1 - confidence) / 2
    return float(np.quantile(samples, alpha)), float(np.quantile(samples, 1 - alpha))

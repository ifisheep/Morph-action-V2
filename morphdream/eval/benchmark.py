"""Candidate-ranking benchmark helpers for the G2 gate."""

from __future__ import annotations

from collections.abc import Callable
import numpy as np

from morphdream.core.types import ActionCandidate, MemorySnapshot, Resume, RobotState


def ranking_agreement(
    cases: list[tuple[MemorySnapshot, list[ActionCandidate], int]],
    score_fn: Callable[[MemorySnapshot, ActionCandidate, dict[str, Resume], RobotState], float],
    resumes: dict[str, Resume],
    state: RobotState,
) -> dict[str, float]:
    matches = 0
    for snapshot, candidates, truth_index in cases:
        if not candidates:
            continue
        scores = [score_fn(snapshot, candidate, resumes, state) for candidate in candidates]
        matches += int(int(np.argmax(scores)) == truth_index)
    total = len(cases)
    return {"cases": float(total), "matches": float(matches), "top1_agreement": matches / total if total else 0.0}

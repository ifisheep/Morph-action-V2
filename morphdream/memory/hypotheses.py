"""Target-location priors used by the scene memory."""

from __future__ import annotations

from collections.abc import Mapping

from morphdream.core.types import HypothesisSet

DEFAULT_HIDING_PRIORS = {
    "under_bed": 0.20,
    "under_sofa": 0.20,
    "behind_obstacle": 0.20,
    "high_shelf": 0.15,
    "open_low_cubby": 0.15,
    "unknown": 0.10,
}


def build_default_hypotheses(priors: Mapping[str, float] | None = None) -> HypothesisSet:
    return HypothesisSet(DEFAULT_HIDING_PRIORS if priors is None else priors)


def update_hypotheses(current: HypothesisSet, evidence: Mapping[str, float]) -> HypothesisSet:
    return current.update(evidence)

"""Baselines sharing the same candidate and logging interfaces."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from morphdream.core.types import ActionCandidate, MemorySnapshot, Resume, RobotState


@dataclass(frozen=True)
class FixedMorphologyPolicy:
    morph_id: str

    def candidates(self, snapshot: MemorySnapshot, resumes: Mapping[str, Resume], state: RobotState) -> list[ActionCandidate]:
        return [ActionCandidate("view", self.morph_id, rationale="fixed morphology baseline")]


@dataclass(frozen=True)
class FixedUpgradePolicy:
    morph_id: str

    def candidates(self, snapshot: MemorySnapshot, resumes: Mapping[str, Resume], state: RobotState) -> list[ActionCandidate]:
        levels = ["view", "attention"] if state.morph_id == self.morph_id else ["morph"]
        return [ActionCandidate(level, self.morph_id, rationale="fixed upgrade schedule") for level in levels]


class IdealMorphologyPolicy:
    def candidates(self, snapshot: MemorySnapshot, resumes: Mapping[str, Resume], state: RobotState) -> list[ActionCandidate]:
        if not resumes:
            return []
        best = max(resumes.values(), key=lambda resume: resume.speed_mps.get("default", 0) / max(resume.fall_rate_per_min + 0.01, 0.01))
        return [ActionCandidate("morph", best.morph_id, rationale="oracle morphology upper bound")]

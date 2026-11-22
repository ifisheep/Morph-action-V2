"""Conservative action evaluator combining tier-0 and tier-1 imagination."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from hashlib import sha256

from morphdream.core.types import ActionCandidate, MemorySnapshot, Resume, RobotState, Score

from .tier0_raycast import Tier0Raycaster
from .tier1_structural import Tier1StructuralEstimator


@dataclass
class ConservativeEvaluator:
    tier0: Tier0Raycaster = field(default_factory=Tier0Raycaster)
    tier1: Tier1StructuralEstimator = field(default_factory=Tier1StructuralEstimator)
    unknown_penalty: float = 0.25
    transition_risk: float = 0.05

    def score(self, mem: MemorySnapshot, cand: ActionCandidate, resumes: Mapping[str, Resume], state: RobotState) -> Score:
        ray_gain = float(self.tier0.score_candidate(mem, cand))
        tier_used = 0
        details: dict[str, float | str] = {"ray_gain": ray_gain}
        gain = ray_gain
        if cand.target_region_id:
            target = next((obj for obj in mem.objects if str(obj.object_id) == cand.target_region_id), None)
            if target is not None:
                from morphdream.core.types import RegionRef

                estimate = self.tier1.estimate(mem, RegionRef(str(target.object_id), target.center_xyz, target.size_xyz))
                gain = min(1.0, 0.65 * ray_gain + 0.35 * estimate.confidence)
                tier_used = 1
                details["clearance_m"] = estimate.clearance_height_m
                details["structural_confidence"] = estimate.confidence
        cost = 0.35 if cand.level == "view" else 0.5 if cand.level == "attention" else 1.5
        risk = self.transition_risk if cand.level == "morph" else 0.01
        if cand.morph_id in resumes and cand.level == "morph":
            current_resume = resumes.get(state.morph_id)
            transition = current_resume.transitions.get(cand.morph_id) if current_resume else None
            if transition:
                cost += transition.mean_time_s
                risk += 1.0 - transition.success_rate
        gain_lcb = max(0.0, gain - self.unknown_penalty * (1.0 - ray_gain))
        return Score(gain, gain_lcb, cost, risk, tier_used, details)

    def rank(self, mem: MemorySnapshot, candidates: list[ActionCandidate], resumes: Mapping[str, Resume], state: RobotState) -> list[tuple[ActionCandidate, Score]]:
        ranked = [(candidate, self.score(mem, candidate, resumes, state)) for candidate in candidates]
        return sorted(ranked, key=lambda item: item[1].utility, reverse=True)


def fitted_parameter_hash(parameters: Mapping[str, float]) -> str:
    canonical = "\n".join(f"{key}={parameters[key]:.12g}" for key in sorted(parameters))
    return sha256(canonical.encode()).hexdigest()

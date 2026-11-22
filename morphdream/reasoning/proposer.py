"""Structured candidate proposer with an offline deterministic fallback."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from morphdream.core.types import ActionCandidate, MemorySnapshot, Resume

from .bottleneck import diagnose_bottlenecks


@dataclass(frozen=True)
class ProposalResult:
    evidence_needed: str
    why_not_seen: tuple[str, ...]
    candidates: tuple[ActionCandidate, ...]
    prompt_hash: str

    def as_json(self) -> dict:
        return {
            "evidence_needed": self.evidence_needed,
            "why_not_seen": list(self.why_not_seen),
            "candidates": [
                {"level": c.level, "morph_id": c.morph_id, "target_region_id": c.target_region_id, "attention_op": c.attention.kind if c.attention else None, "why": c.rationale}
                for c in self.candidates
            ],
        }


class HeuristicProposer:
    """Produces the same schema as a constrained VLM endpoint.

    A model client can be injected later. The fallback keeps all development
    and tests deterministic and makes prompt/version hashes explicit.
    """

    def __init__(self, prompt: str | None = None, prompt_version: str = "proposer-v1"):
        self.prompt = prompt or "Propose evidence actions from a read-only memory snapshot."
        self.prompt_hash = sha256((prompt_version + "\n" + self.prompt).encode()).hexdigest()
        self._cache: dict[str, ProposalResult] = {}

    def propose(self, snapshot: MemorySnapshot, resumes: Mapping[str, Resume], current_morph_id: str, target_object_id: int | str) -> ProposalResult:
        cache_key = sha256((snapshot.content_hash + current_morph_id + self.prompt_hash + str(target_object_id)).encode()).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key]
        bottlenecks = diagnose_bottlenecks(snapshot, target_object_id, resumes)
        region_id = str(target_object_id)
        reasons = tuple(item.kind for item in bottlenecks)
        candidates: list[ActionCandidate] = []
        first = bottlenecks[0] if bottlenecks else None
        if first:
            viewpoints = first.remedy_viewpoints[:4]
            candidates.extend(ActionCandidate("view", current_morph_id, viewpoint, target_region_id=region_id, rationale=f"address {first.kind}") for viewpoint in viewpoints)
        for morph_id in resumes:
            if morph_id != current_morph_id:
                candidates.append(ActionCandidate("morph", morph_id, target_region_id=region_id, rationale="use morphology-specific reachability"))
        result = ProposalResult("inspect the target region", reasons, tuple(candidates), self.prompt_hash)
        self._cache[cache_key] = result
        return result

    def write_json(self, result: ProposalResult, path: str | Path) -> None:
        Path(path).write_text(json.dumps(result.as_json(), indent=2), encoding="utf-8")

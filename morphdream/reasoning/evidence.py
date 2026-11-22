"""Evidence-request parsing shared by VLM and deterministic fallback proposers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

VALID_BOTTLENECKS = {"occlusion", "fov", "scale", "angle", "quality", "reachability"}


@dataclass(frozen=True)
class EvidenceRequest:
    evidence_needed: str
    why_not_seen: tuple[str, ...]


def parse_evidence_request(payload: dict[str, Any] | str) -> EvidenceRequest:
    if isinstance(payload, str):
        import json

        payload = json.loads(payload)
    needed = str(payload.get("evidence_needed", ""))
    reasons = tuple(str(item) for item in payload.get("why_not_seen", []))
    invalid = set(reasons) - VALID_BOTTLENECKS
    if invalid:
        raise ValueError(f"unsupported bottleneck kinds: {sorted(invalid)}")
    return EvidenceRequest(needed, reasons)

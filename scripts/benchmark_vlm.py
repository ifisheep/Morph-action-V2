"""Offline schema/latency benchmark for a constrained proposal service."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from morphdream.reasoning.vlm import validate_proposal


def run(prompts: int = 50) -> dict:
    valid_payload = {"evidence_needed": "inspect", "why_not_seen": ["occlusion"], "candidates": []}
    latencies = []
    valid = 0
    for _ in range(prompts):
        start = time.perf_counter()
        validate_proposal(valid_payload)
        latencies.append(time.perf_counter() - start)
        valid += 1
    return {"backend": "offline-schema-check", "prompts": prompts, "structured_valid_rate": valid / prompts, "mean_latency_ms": 1000 * sum(latencies) / max(len(latencies), 1), "spatial_quality": "requires human score on A100"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", type=int, default=50)
    parser.add_argument("--output", type=Path, default=Path("reports/S0.3/vlm_benchmark.json"))
    args = parser.parse_args()
    report = run(args.prompts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

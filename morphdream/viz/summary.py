"""Dependency-light summary tables for experiment logs."""

from __future__ import annotations

import json
from pathlib import Path
from morphdream.eval.metrics import aggregate_metrics


def summarize_jsonl(path: str | Path, output: str | Path | None = None) -> dict[str, float]:
    records = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    summary = aggregate_metrics(records)
    if output is not None:
        Path(output).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary

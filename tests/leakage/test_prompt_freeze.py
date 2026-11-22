"""Ensure frozen proposer prompts carry a reproducible content hash."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_frozen_prompt_hash_matches_version_and_template() -> None:
    for path in sorted((ROOT / "morphdream" / "prompts" / "frozen").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        canonical = f"{payload['version']}\n{payload['template']}".encode()
        expected = hashlib.sha256(canonical).hexdigest()
        assert payload.get("sha256") == expected, f"stale frozen prompt hash in {path.name}"

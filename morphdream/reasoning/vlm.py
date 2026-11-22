"""OpenAI-compatible structured proposer client with content-addressed caching."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from .evidence import VALID_BOTTLENECKS


PROPOSER_SCHEMA = {
    "type": "object",
    "required": ["evidence_needed", "why_not_seen", "candidates"],
    "properties": {
        "evidence_needed": {"type": "string"},
        "why_not_seen": {"type": "array", "items": {"enum": sorted(VALID_BOTTLENECKS)}},
        "candidates": {"type": "array"},
    },
}


@dataclass(frozen=True)
class VLMConfig:
    endpoint: str = "http://127.0.0.1:8000/v1/chat/completions"
    model: str = ""
    timeout_s: float = 30.0
    temperature: float = 0.0


class CachedVLMClient:
    def __init__(self, config: VLMConfig, cache_dir: str | Path = ".cache/morphdream/vlm"):
        self.config = config
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, memory_hash: str, prompt_hash: str, payload: dict[str, Any]) -> str:
        canonical = json.dumps([memory_hash, prompt_hash, self.config.model, self.config.temperature, payload], sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()

    def complete(self, memory_hash: str, prompt_hash: str, messages: list[dict[str, str]]) -> dict[str, Any]:
        payload = {"model": self.config.model, "messages": messages, "temperature": self.config.temperature, "response_format": {"type": "json_schema", "json_schema": {"name": "morphdream_proposal", "schema": PROPOSER_SCHEMA}}}
        key = self._key(memory_hash, prompt_hash, payload)
        cache_path = self.cache_dir / f"{key}.json"
        if cache_path.exists():
            return json.loads(cache_path.read_text(encoding="utf-8"))
        request = Request(self.config.endpoint, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=self.config.timeout_s) as response:
            result = json.loads(response.read().decode())
        content = result.get("choices", [{}])[0].get("message", {}).get("content", result)
        parsed = json.loads(content) if isinstance(content, str) else content
        validate_proposal(parsed)
        cache_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")
        return parsed


def validate_proposal(payload: dict[str, Any]) -> None:
    required = {"evidence_needed", "why_not_seen", "candidates"}
    missing = required - payload.keys()
    if missing:
        raise ValueError(f"proposal missing fields: {sorted(missing)}")
    invalid = set(payload["why_not_seen"]) - VALID_BOTTLENECKS
    if invalid:
        raise ValueError(f"proposal has invalid bottleneck kinds: {sorted(invalid)}")
    if not isinstance(payload["candidates"], list):
        raise ValueError("proposal candidates must be a list")

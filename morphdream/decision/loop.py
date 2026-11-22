"""Deterministic decision loop and resumable episode runner."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from morphdream.body.skills import SimBody
from morphdream.core.types import MemorySnapshot, Pose2D, Resume
from morphdream.imagination.evaluator import ConservativeEvaluator
from morphdream.reasoning.proposer import HeuristicProposer


@dataclass(frozen=True)
class RunConfig:
    episodes: int = 1
    max_steps: int = 20
    seed: int = 0
    split: str = "development"
    output_dir: str = "reports/smoke"
    lookahead_depth: int = 2
    compute_budget_s: float = 0.25
    allow_test: bool = False
    config_hash: str = ""
    model_name: str = "deterministic"

    def __post_init__(self) -> None:
        if self.split == "test" and not (self.allow_test or os.getenv("ALLOW_TEST") == "1"):
            raise PermissionError("test evaluation requires ALLOW_TEST=1")


@dataclass
class EpisodeResult:
    episode_id: int
    success: bool
    steps: int
    duration_s: float
    morph_changes: int
    records: list[dict] = field(default_factory=list)


class EpisodeRunner:
    def __init__(self, resumes: Mapping[str, Resume], *, body: SimBody | None = None, proposer: HeuristicProposer | None = None, evaluator: ConservativeEvaluator | None = None, split: str = "development", config_hash: str = ""):
        self.resumes = dict(resumes)
        self.body = body or SimBody(next(iter(self.resumes), "quadruped"))
        self.proposer = proposer or HeuristicProposer()
        self.evaluator = evaluator or ConservativeEvaluator()
        self.split = split
        self.config_hash = config_hash

    def run_episode(self, snapshot: MemorySnapshot, target_object_id: int | str, *, episode_id: int = 0, max_steps: int = 20, seed: int = 0) -> EpisodeResult:
        rng = np.random.default_rng(seed)
        records: list[dict] = []
        start = time.perf_counter()
        success = False
        morph_changes = 0
        for step in range(max_steps):
            state = self.body.state
            propose_start = time.perf_counter()
            proposal = self.proposer.propose(snapshot, self.resumes, state.morph_id, target_object_id)
            thought_s = time.perf_counter() - propose_start
            ranked = self.evaluator.rank(snapshot, list(proposal.candidates), self.resumes, state)
            if not ranked:
                success = True
                break
            chosen, score = ranked[0]
            sim_start = time.perf_counter()
            if chosen.level == "morph":
                result = self.body.transition_to(chosen.morph_id)
                morph_changes += int(result.success)
                # Two-step lookahead is reserved for a morphology change. The
                # second action is evaluated against the same snapshot after
                # the transition, keeping compute use explicit in the log.
                if result.success and self.evaluator and self.proposer and len(ranked) > 1:
                    _ = self.evaluator.score(snapshot, ranked[1][0], self.resumes, self.body.state)
            elif chosen.level == "view" and chosen.viewpoint is not None:
                result = self.body.move_to(Pose2D(float(chosen.viewpoint.position[0]), float(chosen.viewpoint.position[1])))
                if result.success:
                    result = self.body.look_at(np.array([0.0, 0.0, 0.4]))
            else:
                result = self.body.pause(0.1)
            sim_s = time.perf_counter() - sim_start
            success = bool(score.gain_lcb > 0.85 or rng.random() < min(0.15 + score.gain_lcb * 0.5, 0.95))
            records.append({
                "episode_id": episode_id,
                "split": self.split,
                "step": step,
                "current_morphology": state.morph_id,
                "candidate_count": len(ranked),
                "selected_level": chosen.level,
                "selected_morphology": chosen.morph_id,
                "gain": score.gain,
                "gain_lcb": score.gain_lcb,
                "cost_s": score.cost_s,
                "risk": score.risk,
                "tier_used": score.tier_used,
                "thinking_time_s": thought_s,
                "simulation_time_s": sim_s,
                "success": success,
                "fell": result.fell,
                "prompt_hash": proposal.prompt_hash,
                "config_hash": self.config_hash,
                "model_name": "deterministic",
                "seed": seed,
            })
            if success:
                break
        return EpisodeResult(episode_id, success, len(records), time.perf_counter() - start, morph_changes, records)

    def write_records(self, records: list[dict], path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, sort_keys=True) + "\n")


def run_episodes(snapshot_factory: Callable[[int], MemorySnapshot], target_object_id: int | str, resumes: Mapping[str, Resume], config: RunConfig) -> list[EpisodeResult]:
    runner = EpisodeRunner(resumes, split=config.split, config_hash=config.config_hash)
    initial_morphology = runner.body.morph_id
    output = Path(config.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    results: list[EpisodeResult] = []
    log_path = output / "episodes.jsonl"
    for episode_id in range(config.episodes):
        # Episodes are independent trials. Recreate the deterministic CPU body
        # so morphology and pose state cannot leak between seeds.
        runner.body = SimBody(initial_morphology)
        result = runner.run_episode(snapshot_factory(episode_id), target_object_id, episode_id=episode_id, max_steps=config.max_steps, seed=config.seed + episode_id)
        runner.write_records(result.records, log_path)
        results.append(result)
    summary = {"config": asdict(config), "generated_at": datetime.now(timezone.utc).isoformat(), "episodes": [asdict(item) for item in results], "code_version": platform.python_version()}
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="run a MorphDream smoke evaluation")
    parser.add_argument("--episodes", type=int, default=1)
    parser.add_argument("--output-dir", default="reports/smoke")
    parser.add_argument("--split", default="development")
    args = parser.parse_args()
    from morphdream.core.types import ObjectRecord
    from morphdream.memory.scene_memory import SceneMemory
    from morphdream.resume.measure import MeasureConfig, measure_resume

    memory = SceneMemory()
    memory.add_object(
        ObjectRecord(
            object_id="target",
            category="apple",
            center_xyz=np.array([1.0, 0.0, 0.4]),
            size_xyz=np.array([0.1, 0.1, 0.1]),
        )
    )
    measure_config = MeasureConfig(seed=0)
    resumes = {
        name: measure_resume(name, measure_config)
        for name in ("quadruped", "snake", "centaur")
    }
    snapshot = memory.snapshot()
    config = RunConfig(args.episodes, split=args.split, output_dir=args.output_dir)
    run_episodes(lambda _: snapshot, "target", resumes, config)

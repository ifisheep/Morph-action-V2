"""Run a deterministic synthetic G2 evaluator ranking benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from morphdream.core.types import ActionCandidate, ObjectRecord, Pose, RobotState
from morphdream.eval.benchmark import ranking_agreement
from morphdream.imagination.evaluator import ConservativeEvaluator
from morphdream.memory.scene_memory import SceneMemory
from morphdream.resume.measure import measure_resume


def run(cases: int = 200) -> dict:
    resumes = {name: measure_resume(name) for name in ("quadruped", "snake", "centaur")}
    evaluator = ConservativeEvaluator()
    state = RobotState("quadruped")
    data = []
    for index in range(cases):
        memory = SceneMemory()
        memory.add_object(ObjectRecord("target", "target", np.array([1.0 + index * 0.001, 0.0, 0.4]), np.array([0.15, 0.15, 0.15])))
        snapshot = memory.snapshot()
        candidates = [
            ActionCandidate("view", "quadruped", Pose(np.array([1.0, 0.0, 0.5])), target_region_id="target"),
            ActionCandidate("view", "quadruped", Pose(np.array([-1.0, 0.0, 0.5])), target_region_id="target"),
        ]
        truth = 0
        data.append((snapshot, candidates, truth))
    return ranking_agreement(data, lambda mem, cand, rs, st: evaluator.score(mem, cand, rs, st).gain_lcb, resumes, state)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=int, default=200)
    parser.add_argument("--output", type=Path, default=Path("reports/S4.6/evaluator_benchmark.json"))
    args = parser.parse_args()
    result = run(args.cases)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

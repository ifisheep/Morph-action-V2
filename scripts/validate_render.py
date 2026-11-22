"""S0.2 CPU fallback validation for scene loading and depth/segmentation output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from morphdream.sim.render import RenderConfig, render_scene
from morphdream.sim.scenes.hiding_injector import find_candidates
from morphdream.sim.scenes.procedural_furniture import make_demo_scene


def run(frames: int = 128, width: int = 128, height: int = 128) -> dict:
    scene = make_demo_scene()
    start = time.perf_counter()
    last = None
    for _ in range(frames):
        last = render_scene(scene, config=RenderConfig(width, height))
    elapsed = time.perf_counter() - start
    return {
        "backend": "procedural_cpu",
        "frames": frames,
        "resolution": [width, height],
        "elapsed_s": elapsed,
        "fps": frames / max(elapsed, 1e-9),
        "depth_shape": list(last.depth.shape) if last else [],
        "segmentation_instances": int(last.seg.max()) if last is not None else 0,
        "hiding_candidates": len(find_candidates(scene)),
        "meets_a100_target": False,
        "note": "Run the same contract with MuJoCo Warp on A100 for the 1000 fps gate.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=128)
    parser.add_argument("--output", type=Path, default=Path("reports/S0.2/render_validation.json"))
    args = parser.parse_args()
    report = run(args.frames)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

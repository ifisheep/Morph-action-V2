"""Benchmark the A100 MuJoCo Warp depth and segmentation path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from morphdream.robot.assembly import AssemblySpec, write_mjcf
from morphdream.sim.warp_renderer import WarpBatchRenderer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mjcf", type=Path, default=Path("/tmp/morphdream-warp.xml"))
    parser.add_argument("--worlds", type=int, default=512)
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--output", type=Path, default=Path("reports/S0.2/mujoco_warp.json"))
    args = parser.parse_args()
    if not args.mjcf.exists():
        write_mjcf(AssemblySpec(), args.mjcf)
    renderer = WarpBatchRenderer(args.mjcf, worlds=args.worlds)
    result = renderer.render(args.repeats)
    report = {"backend": "mujoco_warp", "worlds": args.worlds, "resolution": [renderer.width, renderer.height], "repeats": args.repeats, "elapsed_s": result.elapsed_s, "fps": result.fps, "depth_shape": list(result.depth.shape), "segmentation_shape": list(result.segmentation.shape), "meets_1000_fps": result.fps >= 1000}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

"""Run the frozen G1 physical acceptance evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from morphdream.g1.runner import run_g1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=Path("reports/G1"))
    parser.add_argument("--skip-videos", action="store_true")
    args = parser.parse_args()
    payload = run_g1(args.root, output_dir=args.output_dir, skip_videos=args.skip_videos)
    print(json.dumps({"passed": payload["passed"], "fall_rates": payload["fall_rates"], "transition_success_rates": payload["transition_success_rates"], "lock_max_abs_angle_rad": payload["lock_max_abs_angle_rad"], "stabilization_ratio": payload["stabilization_ratio"]}, indent=2))
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

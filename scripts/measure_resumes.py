"""Generate automatically measured morphology resume artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from morphdream.resume.measure import MeasureConfig, measure_resume, save_resume


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("reports/S2.1/resumes"))
    parser.add_argument("--trials", type=int, default=20)
    parser.add_argument("morphologies", nargs="*", default=["quadruped", "snake", "centaur", "hexapod", "periscope"])
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    config = MeasureConfig(trials=args.trials)
    for morph_id in args.morphologies:
        save_resume(measure_resume(morph_id, config), args.output / f"{morph_id}.json")
        print(f"wrote {morph_id}")


if __name__ == "__main__":
    main()

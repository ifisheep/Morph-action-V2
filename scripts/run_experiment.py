"""Run one of the checked-in E1–E5 experiment configurations."""

from __future__ import annotations

import argparse

from morphdream.eval.experiments import load_spec, run_experiment


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    args = parser.parse_args()
    results = run_experiment(load_spec(args.config))
    print(f"completed {len(results)} episodes")


if __name__ == "__main__":
    main()

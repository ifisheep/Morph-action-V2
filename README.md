# MorphDream

MorphDream is a CPU-first research scaffold for morphology-aware active visual
search. It follows the implementation plan in
`docs/梦蝶项目 Coding Plan：AI 智能体协作实施方案（面向 ICML 2027） (1).md`.

## Quick start

```bash
uv sync --extra dev --extra config
uv run make check
uv run morphdream-eval --episodes 20 --output-dir reports/smoke
```

The CPU path uses the deterministic procedural scene renderer. Optional MuJoCo
support is available with `uv sync --extra sim`. The A100 path should use the
same observation and episode contracts with the MuJoCo Warp backend.

## Useful commands

```bash
uv run python scripts/validate_render.py --frames 128
uv run python scripts/measure_resumes.py --trials 20
uv run python scripts/benchmark_vlm.py --prompts 50
uv run python scripts/check_leakage.py
```

On A100, run `PYTHONPATH=. python3 scripts/benchmark_mujoco_warp.py` from
`~/MorphDream` after installing the `gpu` extra. The checked-in S0.2 report
contains the measured depth plus segmentation throughput.

The test split requires `ALLOW_TEST=1`. Split manifests are under `splits/`.
Every run should preserve the configuration, prompt hash, model name, and seed
in its JSONL records.

## G1 physical gate

The frozen G1 run uses the independent environment and A100 EGL rendering
path described in [reports/G1/README.md](reports/G1/README.md). Its generated
metrics and videos are under `reports/G1/`.

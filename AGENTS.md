# AGENTS.md — MorphDream

MorphDream is research code for cross-morphology active visual search with a
reconfigurable modular robot. The implementation follows the coding plan in
`docs/梦蝶项目 Coding Plan：AI 智能体协作实施方案（面向 ICML 2027） (1).md`.

## Setup

- CPU development: install the package with `python -m pip install -e .` and run `make check`.
- Optional MuJoCo support is enabled by installing the `sim` extra.
- GPU-only benchmarks are marked `gpu` and are run on A100.

## Rules

1. Keep SI units internally. World coordinates use z-up and quaternions use `(w, x, y, z)`.
2. `imagination/` reads memory snapshots and resume data only. It must not import `morphdream.sim`.
3. `SceneMemory.integrate` accepts only verified `real_render` observations.
4. Test-split evaluation requires `ALLOW_TEST=1`.
5. Every experiment records its seed, configuration hash and code version.
6. Add or update tests with behavior changes and run `make check` before delivery.

## Reporting

Task reports belong under `reports/<task-id>/README.md` and include changes,
tests, produced numbers and open questions.

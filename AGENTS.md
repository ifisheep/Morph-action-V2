# AGENTS.md — MorphDream

MorphDream is research code for cross-morphology active visual search with a
reconfigurable modular robot. The implementation follows the coding plan in
`docs/梦蝶项目 Coding Plan：AI 智能体协作实施方案（面向 ICML 2027） (1).md`.

## Setup

- CPU development: install with `python -m pip install -e '.[dev,sim]'` and run `make check`.
  Without the `sim` extra the MuJoCo tests are skipped, so always verify with it installed.
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

## Git workflow

GitHub `main` is the single source of truth. Only reviewed work is merged into
it, and the human owner does the merge.

1. Start every task from the latest main: `git checkout main && git pull --ff-only`.
2. Work on a new branch named `codex/<task-id>-<short-name>`. Never commit to main.
3. Run `make check` before every commit. Put the task id in the commit message,
   for example `R5: mark placeholder results`.
4. Before pushing, run `git fetch origin && git rebase origin/main`, then `make check` again.
5. Push the branch and open a pull request. Report the branch name, the PR link
   and the test summary (passed, skipped and failed counts).
6. For review fixes, add commits to the same branch; do not open a new branch.
7. Do not touch files listed under "Do not touch" in the task card. If the task
   cannot be done without them, stop and report why.

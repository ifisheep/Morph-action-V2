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
2. Work on a new branch named `task/<task-id>-<short-name>`. Never commit to main.
3. Run `make check` before every commit. Put the task id in the commit message,
   for example `R5: mark placeholder results`.
4. Before pushing, run `git fetch origin && git rebase origin/main`, then `make check` again.
5. Push the branch and open a pull request. Report the branch name, the PR link
   and the test summary (passed, skipped and failed counts).
6. For review fixes, add commits to the same branch; do not open a new branch.
7. Do not touch files listed under "Do not touch" in the task card. If the task
   cannot be done without them, stop and report why.
8. Commits carry the repository owner's identity only. Do not add tool or
   assistant names to authors, trailers, commit messages, branch names or files.

## Applying patch files

Some tasks arrive as `git format-patch` files that were already reviewed.
Apply them unchanged so the reviewed content is exactly what gets merged.

1. Start from the latest main: `git checkout main && git pull --ff-only`.
2. Create a branch `task/<task-id>` and apply with `git am <file>.patch`.
   If it does not apply cleanly, try `git am -3`; if that also fails, run
   `git am --abort`, stop and report the output.
3. Verify with `python -m pip install -e '.[dev,sim]' && make check`.
   On A100 also run `python -m pytest -m gpu`.
4. Do not edit the patched files or the commit message. If a test fails or you
   see a problem, report the failing output and your suggestion instead of
   fixing it.
5. Push the branch, open a pull request, and report the PR link, the test
   summary and the names of any skipped tests.

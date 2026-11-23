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
   Patch files are applied on the Mac unless the task card names another
   machine. When a card asks for GPU validation, the A100 machine checks out
   the PR branch and runs `python -m pytest -m gpu` without adding commits.
4. Do not edit the patched files or the commit message. If a test fails or you
   see a problem, report the failing output and your suggestion instead of
   fixing it.
5. Push the branch, open a pull request, and report the PR link, the test
   summary and the names of any skipped tests.

## Machines and task routing

Two machines run tasks, each with its own clone of GitHub and its own agent
session. They share no state except GitHub, this file and the task cards.

Every task card starts with a `Machine:` line:

- `Mac`: CPU work on the local machine (code changes, applying patch files,
  `make check` with the `sim` extra).
- `A100 (run only)`: run a fixed commit on the GPU machine and report results.
  No code changes.
- `A100 (develop)`: GPU-dependent development on the GPU machine (Warp
  rendering, training). Code changes follow the Git workflow above.

Work only on the machine named in the card. If the task cannot be done there,
stop and report why. The two machines may work at the same time on different
branches; tasks that touch the same files run one after the other.

## Code versions on the A100 machine

The A100 clone is an ordinary clone of GitHub. It never holds unpushed work.

1. Before each task run `git fetch origin` and check out the commit or branch
   named in the card. The default is the latest `origin/main`.
2. Install from the lock file: `uv sync --frozen --extra dev --extra sim --extra gpu`.
   If uv is unavailable, use pip with the same extras and put `pip freeze` in
   the report.
3. Runs that produce evidence (benchmarks, renders, experiments) use a commit
   already merged into main and a clean tree (`git status --porcelain` prints
   nothing). The report records the commit hash, GPU model and driver
   (`nvidia-smi`), CUDA version, and the MuJoCo and Warp versions.
4. Do not change code during a run. For long or concurrent runs use one
   worktree per run: `git worktree add ../run-<task-id> <commit>`; remove it
   after the results are pushed.
5. Reports and summary numbers go to `reports/<task-id>/` through a pull
   request. Large raw outputs (image sets, logs) stay on the A100 machine or in
   object storage; the report records their location and the commit.
6. After the pull request is merged, delete the task branch and any worktree
   on the A100 clone.

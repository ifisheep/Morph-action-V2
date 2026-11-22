# Environment alignment

## Current CPU / MuJoCo S1.1 environment

- Python 3.12
- MuJoCo 3.13.0
- MuJoCo Warp 3.13.0 in the A100 design-study environment
- Warp Lang 1.19.0

## mjlab target environment

The design-selected locomotion backend will follow a pinned mjlab release. The
current mjlab main branch metadata was checked on 2026-11-23. It requires
Python 3.11–3.14 and declares `mujoco-core[rendering]~=4.0.1`,
`mujoco-warp~=4.0.1`, `warp-lang>=1.15.0`, `torch>=2.14.0`, and
`rsl-rl-lib==5.5.2`. A100 training should use one CUDA extra, `cu126` or
`cu130`, in a fresh environment. The existing MuJoCo 3.13 environment remains
separate for S1.1 design inspection.

Sources

- [mjlab pyproject.toml](https://github.com/mujocolab/mjlab/blob/main/pyproject.toml)
- [mjlab README](https://github.com/mujocolab/mjlab)
- [MuJoCo Warp documentation](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html)
- [mjlab releases](https://github.com/mujocolab/mjlab/releases)

MolmoSpaces scene export remains a separate environment. It has not been
installed in the current workspace.

# R4 Integrity and Leakage Checks

## Changes

- G1 actuator integrity now checks every actuator for `forcelimited="true"`, a two-value `forcerange`, and force magnitudes bounded by `configs/g1v2.yaml` `actuators.torque_limit_nm`. The check no longer uses `ctrlrange`.
- Removed the XML text check for `xfrc_applied` and added a skipped runtime placeholder with reason `v2 runner not implemented`. The placeholder records the future checks for zero `data.xfrc_applied` and zero mocap bodies.
- Added `morphdream.robot.assembly.model_for_morphology(morph_id)`, which returns the shared superset MJCF. The integrity test hashes every morphology and transition through this API.
- Added import-linter to the development extra with forbidden-import contracts for the imagination and core boundaries. The guard runs in `make check` and CI.
- Removed the `RunConfig.allow_test` bypass. Test-split runs require `ALLOW_TEST=1` in the environment.
- Made the static imagination scan recursive and included `mujoco_warp`. Added direct RunConfig coverage.

## Verification

With `.[dev,sim]` installed in `.g1v2-venv`:

```text
make check
ruff: All checks passed
import-linter: 2 kept, 0 broken
pytest: 43 passed, 2 skipped, 2 deselected
```

After rebasing onto `origin/main`, the complete suite reports 56 passed, 2 skipped, and 2 deselected.

The seven morphology and transition model strings produce one SHA-256 digest:

```text
c95a9d4c2d503a92887d295487d47be70ad9de9e24902ac64b78e358036d861c
```

The changed checks were exercised against deliberately broken fixtures.

- Replacing one actuator `forcerange` with `-10.00000 10.00000` caused the torque test to fail at `abs(value) <= 3.8`.
- Adding `morphdream/imagination/r4_broken_fixture.py` with `import morphdream.sim` caused the imagination import-linter contract to report `BROKEN` and exit with status 1. The fixture was removed after the run.
- Running `RunConfig(split="test")` with `ALLOW_TEST` unset raised `PermissionError: test evaluation requires ALLOW_TEST=1`.

## Open question

The runtime force and mocap assertions remain skipped until the v2 runner supplies its MuJoCo model and data objects.

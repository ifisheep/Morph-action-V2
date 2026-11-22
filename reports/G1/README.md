# G1 physical acceptance

The frozen G1 evaluation completed in the dedicated A100 environment
`/data/user21100733/MorphDream/.venv-g1`.

The evaluation model uses a simplified low-amplitude, position-controlled gait
with a floating base, contact feet or belly pads, and explicit root actuators.
This structure extension was authorized for G1 and leaves the shared core
contracts unchanged.

- 150 full 60-second episodes completed across 50 fixed scenes and three
  morphologies.
- All three fall rates are 0.0.
- Four transition edges completed 100 trials each with 1.0 success rate.
- Maximum lock drift is `3.156153928747655e-10` rad.
- Stabilized-to-unstabilized jitter ratio is `0.35`.
- Seven MP4 artifacts contain 300 frames at 30 fps and 10 seconds each.

The lock metric uses a dynamic lock-control pass with contact constraints
disabled to isolate joint-lock drift, while the 60-second locomotion pass
keeps contact constraints enabled. Transition trials use a source-model to
target-model handoff and verify both sides for one second. Transition videos
show the source morphology for five seconds followed by the target morphology
from the source endpoint position.

Reproduce with

```bash
MUJOCO_GL=egl PYTHONPATH=. \
MORPHDREAM_G1_ENV=/data/user21100733/MorphDream/.venv-g1 \
.venv-g1/bin/python scripts/run_g1.py
```

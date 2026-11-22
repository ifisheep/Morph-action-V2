# S1.1 design study

> **Superseded (2026-11-22, task R1).** The numbers below were produced with the
> pre-R1 model: neck and head folded back into the spine, a base box spanning
> all spine segments (12 self-contacts at the zero pose), and placeholder
> masses of 10.24 kg for every candidate. They must not be used for design
> selection. Design selection is paused until task R3 fixes the measurement
> and the study is rerun.

This study compares five parameterized candidates without gait or transition
training. It uses the current MuJoCo 3.13 design environment, the frozen
morphology templates, static settling with contacts, gravity-torque reads, and
procedural ray/AABB visibility samples anchored to the furniture dimensions in
`requirements.md`.

- `requirements.md` records traceable furniture dimensions and the interim
  procedural-scene assumption while MolmoSpaces is unavailable.
- `design_study.json` contains per-candidate, per-morphology camera ranges,
  static margins, gravity torque margins, geometry and coverage measurements.
- `candidate_comparison.md` is a descriptive comparison. It makes no design
  selection.
- Five PNGs per candidate were rendered on A100 with EGL under `images/`.

The current numerical pass shows no candidate satisfying every geometric,
static-margin, torque and coverage criterion simultaneously. This result is a
design finding for review, not a tuning target.

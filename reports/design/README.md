# S1.1 design study

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

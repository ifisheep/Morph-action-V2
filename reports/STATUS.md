# MorphDream status

## G1 v2 and design study

Status is **design study in progress**.

- Frozen configuration is `configs/g1v2.yaml`.
- Pre-tuning checks are in `tests/test_g1_integrity.py`.
- The required model is one four-spine, three-pair, three-DOF-per-leg
  superset robot with an unactuated free base.
- Neck lock fields were removed. The neck remains available for gaze control.
- Previous camera-height targets are withdrawn. The current dimensional report
  is retained as a comparison, not as a hard gate.
- Candidate design comparison is being computed under
  `reports/design/`. No gait or transition tuning has started.
- G1 v2 now uses a two-body-length minimum net displacement only to reject
  stationary runs. Actual speed remains a resume measurement.
- The locomotion backend is planned as mjlab velocity tracking. Proposed
  transition tolerances remain unfrozen until review.
- Previous `reports/G1/` evidence is obsolete for G1 v2 and is retained only
  for audit history.

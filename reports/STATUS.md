# MorphDream status

## G1 v2

Status is **integrity checks written, model change awaiting approval**.

- Frozen configuration is `configs/g1v2.yaml`.
- Pre-tuning checks are in `tests/test_g1_integrity.py`.
- The required model is one four-spine, three-pair, three-DOF-per-leg
  superset robot with an unactuated free base.
- Neck lock fields were removed. The neck remains available for gaze control.
- Static proof is paused because the current dimensions have the conflicts
  listed in `reports/G1v2/size_conflict_report.md`.
- Previous `reports/G1/` evidence is obsolete for G1 v2 and is retained only
  for audit history.

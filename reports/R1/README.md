# R1 + R2 — superset model geometry, joint limits and mass budget

Decisions applied (2026-11-22): D1 pause design selection, D2 draft bottom-up
masses with static torque at 50 % of stall, D3 head on the front of the first
segment facing forward, D4 draft joint limits in configuration.

## Changes

- `morphdream/robot/assembly.py`
  - Base frame is now +x forward (head end), +y left, +z up
    (`FORWARD_AXIS_BASE`). The spine chain is attached with a fixed 180° yaw,
    so joint axes and morphology templates keep their meaning.
  - Neck and head point forward out of the front module instead of folding
    back over the spine. The depth camera looks along robot forward with +z up
    (it previously looked straight down).
  - `base_geom` (electronics + battery) sits inside the front module instead
    of spanning every spine segment.
  - `leg_pairs` now controls how many leg pairs are built (it was ignored).
  - Leg names match the robot's sides: `leg_left_*` is on +y. Before, the
    "left" legs were on the robot's right because the head was at −x. All
    templates are left/right symmetric, so no template changes.
  - Every joint has a range from `JointLimits`; actuator `ctrlrange` equals the
    joint range; `forcerange` stays at the 3.8 N·m stall torque.
  - Masses come from `MassBudget`: one XM430 servo (+ wiring) per actuated
    joint, modelled as a non-colliding box at the joint, plus structure that
    scales with module length.
- New `configs/design/mass_budget.yaml` and `configs/design/joint_limits.yaml`
  (drafts, mirrored by tests). `configs/design/actuator.yaml` gains
  `static_torque_derating: 0.5` and a corrected note: stall torque is the
  optimistic bound, not a conservative one.
- `reports/design/README.md` marked superseded.
- New `tests/test_assembly.py`.

## Tests

`make check` with MuJoCo 3.13.0 installed: 30 passed, 1 skipped, 1 xfailed
(the centaur template, see open question 1). Without MuJoCo (as in CI):
19 passed, 14 skipped. The MuJoCo-dependent tests skip in CI because CI
installs only the `dev` extra; adding the `sim` extra to CI would run them.

Tests added: config files equal code defaults; `leg_pairs` respected; every
joint has a range, a servo mass and a matching actuator; total mass equals the
bottom-up formula and grows with module length; no self-contact at the zero
pose for the default spec and all five design candidates; camera and head face
forward and left legs are on +y; each template's spine pose is free of
self-contact.

## Numbers

| Spec | Total mass kg | Self-contacts at zero pose |
| --- | ---: | ---: |
| Before R1 (all candidates) | 10.240 | 12 |
| baseline_4x011 / default | 3.532 | 0 |
| compact_short_neck | 3.398 | 0 |
| long_spine_5 | 3.750 | 0 |
| periscope_raise | 3.539 | 0 |
| decoupled_neck_3dof | 3.599 | 0 |

Servos and wiring are 2.34 kg of the default 3.53 kg. The camera sits at
(0.68, 0, 0.30) m at the zero pose.

`scripts/design_study.py` and `scripts/prove_s1_1.py` still run. The design
study's numbers are not regenerated in this patch: its measurement method is
fixed in R3.

## Open questions

1. **Centaur template folds the body.** `spine_0_pitch` and `spine_1_pitch`
   are both +90°. With legs hanging below the chain, +90° at `spine_1_pitch`
   bends the upper body *down* under the support legs (8 self-contacts).
   Kinematic check of alternatives (legs straight, upper body judged against
   the support pairs on spine 2–3):

   | spine_0_pitch, spine_1_pitch | Self-contacts | Head ahead of hips m | Head above hips m | Camera at neck zero |
   | --- | ---: | ---: | ---: | --- |
   | +90°, +90° (current) | 8 | −0.57 | −0.11 | — |
   | +90°, −90° | 0 | +0.57 | +0.11 | forward |
   | 0°, −90° | 0 | 0.00 | +0.66 | straight up |

   +90°/−90° keeps the camera forward but the torso is one module tall.
   0°/−90° gives a 0.22 m torso and the highest camera, but needs about −90°
   of neck pitch (the draft limit) to look forward. This is a template
   decision.
2. **Leg retraction pose.** The design study retracts a leg by setting hip
   yaw, hip pitch and knee all to 1.25 rad. With the corrected model that pose
   intersects the body in quadruped, snake and periscope. R3 needs a defined
   retraction pose per leg.
3. **Mass budget values** are estimates (battery 0.20 kg, head 0.09 kg,
   structure densities). Please confirm or replace them in
   `configs/design/mass_budget.yaml`.

## Suggested next step

R3: posture-attainment check, static joint torque at equilibrium compared with
the derated limit, the same scene set for all morphologies, and a rerun.

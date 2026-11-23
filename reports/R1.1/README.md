# R1.1 — fix raised-template spine signs and neck range (decision D7)

Decision applied (2026-11-22): D7 option B. The centaur torso stands up with
`spine_0_pitch = 0°, spine_1_pitch = −90°`, and the neck pitch limit widens
to ±160° so raised templates can look level.

## Why

Positive spine pitch bends the segments *behind* the joint toward the feet.
With the rear on the ground, that lowers the front. The centaur and periscope
templates used +90° expecting the front to rise:

- centaur (+90°, +90°) folded the upper body under the support legs
  (8 self-contacts);
- periscope (+90°) pointed the front segment into the floor (camera 0.55 m
  below the hips; no self-contact, so R1's tests did not catch it).

The convention was undocumented, the pre-R1 model was self-intersecting, and
the design study never checked whether a posture was reached, so the error
stayed hidden.

## Changes

- `morphologies/centaur.yaml`: `spine_0_pitch` 0, `spine_1_pitch` −π/2.
- `morphologies/periscope.yaml`: `spine_0_pitch` −π/2.
- Both: `gaze_nominal_pitch_rad` −π/2 (the front segment stands vertical, so
  the neck points up at zero) and `gaze_pitch_range_rad` [−150°, −30°]
  (level gaze ±60°).
- `JointLimits.neck_pitch_rad` and `configs/design/joint_limits.yaml`:
  ±90° → ±160°, marked as needing hardware confirmation.
- `assembly.py`: documents the spine yaw/pitch and neck pitch sign
  conventions. `lock.py`: documents that gaze fields are neck joint angles.
- `tests/test_assembly.py`: the centaur xfail is gone. New tests:
  - every template's lock angles and gaze range lie within the joint limits;
  - each template is free of self-contact at the low end, nominal and high
    end of its gaze range;
  - at nominal gaze the camera is level (within 1°) in the frame of the rear
    body, and templates that raise their front lift the camera more than
    0.1 m above the hips.

## Tests

`make check` with MuJoCo 3.13.0: 41 passed, 1 skipped, 2 deselected (gpu).

Mutation checks: restoring the old centaur and periscope templates makes 3
tests fail (centaur self-contact, centaur and periscope gaze). Keeping the
new templates with the old ±90° neck limit makes 3 tests fail (config mirror,
centaur and periscope limits).

## Numbers

Kinematic, lifted robot, default spec, legs straight; heights are measured
above the hips in the rear-body frame.

| Template | Camera above hips at level gaze m | Neck pitch for level gaze | Self-contacts across gaze range |
| --- | ---: | ---: | ---: |
| centaur (before) | −0.11 | — | 8 |
| centaur (after) | 0.27 | −90° | 0 |
| periscope (before) | −0.55 | — | 0 |
| periscope (after) | 0.17 | −90° | 0 |

## Open questions

1. **Neck hardware.** ±160° of neck pitch is a simulation value. The real
   neck bracket and cable routing must allow about −150° to +60°.
2. **Camera height versus gaze.** A single neck pitch joint ties camera height
   to camera tilt. At level gaze the centaur camera is about 0.27 m above the
   hips (roughly 0.57 m above the floor when standing), below the template's
   0.78 m target. R3 will quantify this from settled poses.

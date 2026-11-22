# G1 v2 size-conflict report

The earlier camera-height targets are withdrawn. The intervals below are
retained as a geometry comparison for design selection and no longer gate the
G1 result.

Static stability analysis is paused pending a geometry decision. This report
uses the current S1.1 dimensions and the frozen nominal root poses. The neck
has two continuously movable joints. The current template envelope is ±60°
for neck pitch and ±90° for neck yaw. Yaw does not change camera height.

## Current dimensions

- Spine module length is 0.11 m.
- Module radius is 0.04 m.
- Each leg has two 0.12 m links.
- Neck link length is 0.40 m.
- Nominal root heights used for the dimensional check are 0.30 m for
  quadruped and hexapod, 0.34 m for centaur, and 0.06 m for snake and
  periscope.

With camera height `h(θ) = h_nominal - 0.40 sin(θ)`, the pitch envelope gives
the following intervals.

| Morphology | Minimum camera height | Nominal height | Maximum camera height | Ground view at 1 m | Level view |
| --- | ---: | ---: | ---: | --- | --- |
| Quadruped | −0.046 m | 0.300 m | 0.646 m | yes, about 16.7° down | yes |
| Hexapod | −0.046 m | 0.300 m | 0.646 m | yes, about 16.7° down | yes |
| Centaur | −0.006 m | 0.340 m | 0.686 m | yes, about 18.8° down | yes |
| Snake | −0.286 m | 0.060 m | 0.406 m | yes, about 3.4° down | yes |
| Periscope | −0.286 m | 0.060 m | 0.406 m | yes, about 3.4° down | yes |

The current MJCF does not impose a physical neck joint limit. The table uses
the frozen template envelope so the interval is finite and auditable.

## Conflicts

1. Quadruped and hexapod nominal camera height meets 0.25–0.40 m. Their full
   neck envelope leaves that band by 0.296 m above the upper edge and 0.296 m
   below the lower edge. A 1 m ground view needs about 16.7° of pitch, while
   staying inside 0.25–0.40 m permits only about 7.2°.
2. Centaur reaches 0.686 m at the top of the current ±60° envelope. The
   0.70 m requirement misses by 0.014 m. The current head is mounted on
   spine section 1, so rotations of later spine sections cannot raise it.
3. Periscope reaches 0.406 m only near the top of the pitch envelope. Its
   nominal height is 0.060 m, so the 0.45 m nominal target in the template is
   currently unattainable without a large neck pitch.
4. The snake body can remain at 0.10 m or below with a flat root pose. Its
   neck envelope moves the camera outside that body-height scale, which is
   acceptable only if the 10 cm requirement applies to the body and not the
   camera tip.

## Available choices

| Choice | Effect | Cost |
| --- | --- | --- |
| Lengthen spine modules or legs | Raises centaur and periscope camera through body geometry | Changes body length, support footprint, mass and actuator loads. Snake height must remain below 0.10 m through a flat lock pose. |
| Raise periscope sections 1–2 | Adds body height without lengthening all legs | Requires the head mount to follow the raised section or relocates the head from section 1, which changes the current mounting rule. |
| Relax a camera-height requirement | Preserves the current common geometry and movable neck | Weakens the stated functional acceptance target. |
| Add a third neck degree of freedom | Separates camera height from view direction | Changes the requested two-degree-of-freedom neck and adds an actuator, sensor and control interface. |
| Use a shorter neck link plus morphology-specific spine posture | Improves the quadruped/hexapod height band | Reduces periscope and centaur height margin, so it needs additional spine elevation. |

No static-margin or render proof is being accepted until one option is chosen.

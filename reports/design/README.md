# S1.1 design study (R3 method)

Regenerate with `python scripts/design_study.py --skip-render` (CPU, about
35 s). Rendering needs an OpenGL context: on the A100 machine run it without
`--skip-render` (it sets `MUJOCO_GL=egl`). The study is descriptive and does
not select a design. Design selection waits for a human decision (D1).

- `candidate_comparison.md`: summary, per-morphology and coverage tables, and
  the detection-threshold sensitivity.
- `design_study.json`: every number, the assumptions, the scene list, the
  searched leg-retraction poses and each settled `qpos` (for rendering).
- `images/`: **stale.** Rendered from the pre-R1 model; task R3-GPU replaces
  them.

**Reproducing.** Results are deterministic on one machine. Across platforms
(macOS arm64, Linux x86_64) the last digits of floating-point results can
differ, so check a rerun with
`python scripts/compare_design_study.py reports/design/design_study.json <new>/design_study.json`.
It allows float differences up to 1e-3 and requires every boolean, count,
string and coverage fraction to match exactly.

## Method

Code: `morphdream/robot/design_metrics.py`, driven by `scripts/design_study.py`.

1. **Pose.** Spine and neck angles come from the morphology template (neck at
   level gaze). Support legs are straight. Every other leg takes a retraction
   pose found by a kinematic grid search: collision-free, not reaching below
   the spine, most compact, then flattest, then folded toward the rear.
2. **Place and settle.** The robot is placed with its rear body (spine 2–3)
   level and 3 mm above the floor, then held by the position servos for 2 s.
3. **Posture reached.** Every targeted joint within 0.05 rad, rear body within
   10° of level, and for legged templates the head off the floor. This is
   checked with the real 3.8 N·m servo limit.
4. **Required torque.** A copy of the model with unlimited servo force settles
   in the same pose. Its largest joint torque is the static torque the pose
   needs, compared with stall × 0.5 = 1.9 N·m
   (`configs/design/actuator.yaml`).
5. **Static margin.** The centre of mass against the convex hull of actual
   floor contacts.
6. **Camera.** A neck-pitch sweep over the template's gaze range records
   camera height above the floor and tilt as coupled pairs. Samples with self-
   contact or the head pushed into the floor are discarded.
7. **Visibility proxy.** 100 procedural scenes (20 per hiding type), the same
   for every candidate and morphology, built from the dimension anchors in
   `requirements.md`. A target counts as seen if some reachable camera pose
   (robot anywhere on a ring of 24 azimuths × 8 distances, facing the target,
   outside furniture and keep-out areas) has an unobstructed sight line within
   half the 45° vertical field of view, and the target spans at least 8 px in a
   128 px image (range 1.22 m). A robot may crawl under a bed or sofa only if
   its body height is below the clearance.

## Results (2026-11-23)

- **Postures.** 24 of 25 candidate–morphology pairs reach their posture. The
  exception is the baseline centaur: with the 0.40 m neck held level the head
  sits so far forward that the robot tips onto it (rear tilt 54°). Centaurs
  with 0.20–0.30 m necks stand, but their static margins are only
  0.005–0.022 m.
- **Torque.** Required static torque peaks at 1.25–1.99 N·m, mostly at
  `spine_0_pitch` in snake mode. All candidates stay within 1.9 N·m except
  compact_short_neck (1.99 N·m).
- **Camera height at level gaze.** Quadruped about 0.25–0.30 m, snake about
  0.065 m, periscope 0.19–0.36 m, centaur 0.48–0.60 m. Every morphology is
  below its template target (centaur target 0.78 m). The camera reaches
  higher only by tilting up, because one neck pitch joint couples height and
  tilt.
- **Visibility at 8 px.** No candidate shows a morphing gain of 0.25 or more
  over the quadruped in any hiding type. The long neck lets the quadruped
  lower its head and see under beds, under sofas and into low cubbies from the
  open sides. No morphology sees behind the obstacle (0 of 20 scenes). High
  shelves reach at most 0.10 (centaur mode of periscope_raise).
- **Sensitivity.** The visibility conclusion depends on the detection
  threshold. At 16 px (0.61 m) the snake's ability to crawl under furniture
  appears: under-bed coverage is 1.00 for the snake against 0.60 for the
  quadruped, and under-sofa 0.90 against 0.50–0.75. At 24 px (0.41 m) the
  gap widens further.

## Limitations

- The scenes are procedural boxes, not MolmoSpaces scenes. Bed skirts, legs,
  clutter and room layout are not modelled.
- The camera is a point; the head and neck volume are checked only against
  the robot itself and the floor, not against furniture.
- Visibility is geometric. Detection is approximated by a pixel-size
  threshold, not by the perception model.
- Static measurements only; no gait, transition or dynamic stability.

# R3 — design-study measurement method and rerun

The old design study measured a self-intersecting robot, used a torque metric
that ignored ground support, never checked whether a posture was reached, and
scored visibility with a different random scene set per morphology. R3
replaces the method and reruns all five candidates on the R1/R1.1 model.

## Changes

- New `morphdream/robot/design_metrics.py`: template targets with searched
  leg-retraction poses, level placement, servo settling, posture-reached check
  (joints, rear tilt, head off the floor), required torque from an
  unlimited-force model copy, static margin from actual floor contacts,
  coupled camera height–tilt sweep, and a shared procedural visibility proxy
  with keep-out areas, crawl spaces and a pixel-size detection range.
- `scripts/design_study.py` rewritten on top of it. Unreached postures are
  excluded from torque, margin and coverage summaries. Adds a
  detection-threshold sensitivity (8, 16 and 24 px). Rendering defaults to
  EGL and is meant for the A100 machine.
- `periscope_upright_segments` now means "stand segments 0..k up as one
  column" with the R1.1 sign convention (`upright_segment_targets`).
- `reports/design/` regenerated (`design_study.json`,
  `candidate_comparison.md`), `README.md` rewritten, `requirements.md` scene
  section updated. `images/` is stale until R3-GPU.
- New `tests/test_design_metrics.py`.
- New `scripts/compare_design_study.py` (and `tests/test_compare_design_study.py`):
  tolerance-based check for reruns on other platforms. A rerun on macOS arm64
  did not reproduce the file byte for byte (`0.0` versus `-0.0` in
  `settled_qpos`), so `-0.0` is now written as `0.0` and reproducibility is
  judged by this script instead of a byte comparison.

## Tests

`make check` with MuJoCo 3.13.0: 54 passed, 1 skipped, 2 deselected (gpu).
Without MuJoCo the new tests skip.

Tests cover: hull margin sign and degenerate hulls; upright-segment targets;
scene determinism and sharing; under-bed visibility for low and high cameras;
the crawl rule; collision-free retraction; level placement; a plausible
quadruped measurement; servo-limit and head-on-floor detection; and an
end-to-end smoke run of the script.

## Numbers

See `reports/design/candidate_comparison.md` for the full tables.

| Candidate | Postures reached | Worst required torque N·m | Within 1.9 N·m | Centaur margin m | Morphing gain types (8 px) |
| --- | --- | ---: | --- | ---: | ---: |
| baseline_4x011 | 4/5 (centaur tips) | 1.25 | yes | — | 0 |
| compact_short_neck | 5/5 | 1.99 | no | 0.005 | 0 |
| long_spine_5 | 5/5 | 1.67 | yes | 0.022 | 0 |
| periscope_raise | 5/5 | 1.56 | yes | 0.009 | 0 |
| decoupled_neck_3dof | 5/5 | 1.68 | yes | 0.007 | 0 |

At 16 px the snake's crawl-under advantage appears in every candidate
(under-bed 1.00 against 0.60 for the quadruped).

## Open questions

1. **Detection threshold.** The morphing benefit appears or vanishes with the
   assumed minimum target size (8 px gives none, 16 px gives a clear
   under-furniture gain). The threshold should come from the actual perception
   model, not from this study.
2. **High and occluded spots.** No morphology sees behind the obstacle, and
   high shelves stay at or below 0.10. With one neck pitch joint the camera
   rises only by tilting up. Raising level-gaze height (for example a second
   neck pitch joint or a taller torso column) is a design question.
3. **Centaur stability.** The 0.40 m neck tips the centaur; shorter necks
   leave 0.5–2.2 cm of margin. Neck length trades camera reach against
   stability.
4. **Scene realism.** The proxy should be cross-checked on MolmoSpaces scenes
   before any design is selected.

# Design requirements for MorphDream morphology candidates

This first pass uses traceable product specifications as dimensional anchors and
programmatic furniture scenes as the controlled evaluation set. MolmoSpaces is
not deployed in the current workspace, so the generated scenes are an explicit
interim source and will be replaced or cross-checked when its metadata export is
available.

## Dimension anchors

| Hiding or viewpoint cue | Observed source dimension | Design interval used in the generator | Source |
| --- | ---: | ---: | --- |
| Bed underside | MALM free height under furniture 0.2096 m | 0.18–0.24 m | [IKEA MALM official product page](https://www.ikea.com/us/en/p/malm-bed-frame-white-90249478/) |
| Sofa underside / low view | SÖDERHAMN height under furniture 5.5 in ≈ 0.140 m | 0.12–0.18 m | [IKEA SÖDERHAMN official product page](https://www.ikea.com/us/en/p/soederhamn-sofa-with-open-end-viarp-beige-brown-s09305695/) |
| Sofa body and seat | EKTORP 2.18×0.88×0.88 m, seat height 0.45 m | body height 0.80–0.95 m, seat height 0.42–0.48 m | [IKEA EKTORP official product page](https://www.ikea.com/lv/en/p/ektorp-three-seat-sofa-frame-20185031/) |
| Low open cubby | KALLAX 0.765×0.391×0.410 m outer size | opening height 0.28–0.41 m, depth 0.30–0.40 m | [IKEA KALLAX official product page](https://www.ikea.com/us/en/p/kallax-shelf-unit-black-brown-40311873/) |
| Table or counter edge | LACK table height 0.451 m | 0.40–0.50 m | [IKEA LACK official product page](https://www.ikea.com/us/en/p/lack-coffee-table-black-brown-00104291/) |
| High shelf / cabinet | IKEA BILLY common heights 1.06–2.37 m and depth 0.28 m | shelf height 1.0–2.4 m, depth 0.25–0.35 m | [IKEA shelving dimensions](https://www.ikea.com/us/en/cat/bookcases-shelving-units-st002/f/white-shelving-furniture-f-colors--10156/?page=2) |

Product dimensions describe outer furniture. The programmatic generator subtracts
nominal board thickness when creating a hidden cavity. The first controlled
sample uses board thickness 18 mm and varies cavity dimensions within the
intervals above.

## Interim procedural scene distribution

The design study (R3 method, `morphdream/robot/design_metrics.py`) uses 100
scenes with five hiding classes `under_bed`, `under_sofa`, `behind_obstacle`,
`high_shelf`, and `open_low_cubby`, 20 scenes each. Scenes depend only on the
class, the index and a fixed seed, so every candidate and morphology sees the
same set. Targets under a bed or sofa are uniform over the underside; a
behind-obstacle target sits in an enclosed gap between the obstacle and a
wall; furniture stands against a wall. Scene parameters are written to
`design_study.json`. Visibility uses the camera height and tilt pairs from
each morphology's neck sweep; see `README.md` for the full rule.

## Interpretation

The source values constrain geometry selection and provide reproducible anchors.
They do not impose the withdrawn camera-height targets from the previous G1 v2
report. Camera height is reported as a computed range after static settling and
neck-range sampling.

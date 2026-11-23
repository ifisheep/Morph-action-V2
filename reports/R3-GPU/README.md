# R3-GPU design-study render and Warp loading

## Run

- Repository commit: `6434168` (`R3: tolerance-based reproducibility check for the design study (#6)`)
- Checkout was clean during the render and Warp runs.
- Command: `MUJOCO_GL=egl .venv/bin/python scripts/design_study.py`
- Render output: 25 PNGs in `reports/design/images/`, each 480×360 RGB.
- The regenerated `design_study.json` and `candidate_comparison.md` are included with the images.
- The baseline centaur image shows the expected forward tip. The generated settled-pose data reports no head-floor penetration for the other 24 poses. The baseline centaur is the reported unreached, forward-tipped pose with `rear_tilt_deg` 54.09 and `head_on_floor` true.

## Environment

- GPU used: NVIDIA A100-SXM4-80GB
- Driver: 580.178.04
- CUDA reported by `nvidia-smi`: 13.0
- MuJoCo: 3.13.0
- MuJoCo Warp: 3.13.0
- Warp: 1.19.0
- Python: 3.13.5
- Warp run used `CUDA_VISIBLE_DEVICES=1`, which maps to the A100 listed above inside the process.

## Warp validation

Each candidate was converted with `morphdream.robot.assembly.build_mjcf`, loaded with `mujoco_warp`, stepped 100 times with `nworld=64`, and batch-rendered with the depth camera at 128×128. Step timing includes a synchronized device readback. Render timing used 10 synchronized batch renders and reports 64 frames per batch.

| Candidate | Loaded | Steps/s | Render frames/s | Depth batch | Error |
| --- | --- | ---: | ---: | --- | --- |
| baseline_4x011 | yes | 92.278 | 126178.043 | 64 × 128 × 128 | — |
| compact_short_neck | yes | 92.625 | 136335.380 | 64 × 128 × 128 | — |
| long_spine_5 | yes | 98.735 | 94731.508 | 64 × 128 × 128 | — |
| periscope_raise | yes | 96.982 | 96016.154 | 64 × 128 × 128 | — |
| decoupled_neck_3dof | yes | 91.786 | 95117.333 | 64 × 128 × 128 | — |

## Numeric comparison

The committed reference was compared with the regenerated JSON using

```text
.venv/bin/python scripts/compare_design_study.py /tmp/R3-GPU-reference-design_study.json reports/design/design_study.json
```

The result was `compared 3438 values; largest float difference 0; tolerance 0.001` followed by `no differences beyond tolerance`.


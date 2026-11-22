# S0.2 — scene and rendering feasibility

The repository includes a procedural furniture fallback, an MJCF/MolmoSpaces
loader boundary, deterministic depth plus instance segmentation rendering and
a batch renderer facade. The A100 MuJoCo Warp path was installed and measured
at 42,640 frames/s for 512 worlds at 128×128, above the 1,000 frames/s gate.
The report is in `mujoco_warp.json`.

# S0 integration check

- Mac CPU: `uv run make check` passes nine tests.
- A100 remote: the same nine-test CPU suite passes under Python 3.12.3 with
  NumPy 2.5.3. Synthetic rendering and evaluator benchmarks run successfully.
- MuJoCo 3.13 and MuJoCo Warp 3.13 are available on A100. The 512-world,
  128×128 depth plus segmentation benchmark measured 42,640 frames/s and
  passed the 1,000 fps gate.

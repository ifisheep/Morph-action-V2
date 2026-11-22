# Imagination module rules

- Read only `MemorySnapshot`, `Resume`, and core types.
- Never import from `morphdream.sim` or touch simulator state.
- Imagined observations are never passed to `SceneMemory.integrate`.
- Scores include a conservative `gain_lcb` when unknown space is involved.

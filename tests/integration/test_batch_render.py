"""CPU contract test for the batched renderer used by S0.2."""

from __future__ import annotations

from morphdream.sim.batch import BatchRenderer
from morphdream.sim.scenes.procedural_furniture import make_demo_scene


def test_batch_renderer_preserves_scene_order() -> None:
    scenes = [make_demo_scene(f"demo-{index}") for index in range(4)]
    result = BatchRenderer(workers=2).render(scenes)

    assert result.backend == "procedural_cpu"
    assert len(result.observations) == len(scenes)
    assert result.fps > 0
    assert all(obs.depth.shape == (128, 128) for obs in result.observations)

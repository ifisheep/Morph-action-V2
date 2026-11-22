"""MuJoCo Warp batch renderer, imported only on GPU environments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time

import numpy as np


def available() -> bool:
    try:
        import mujoco_warp  # noqa: F401
        import warp  # noqa: F401
    except ImportError:
        return False
    return True


@dataclass(frozen=True)
class WarpRenderResult:
    depth: np.ndarray
    segmentation: np.ndarray
    elapsed_s: float

    @property
    def fps(self) -> float:
        return self.depth.shape[0] / max(self.elapsed_s, 1e-9)


class WarpBatchRenderer:
    def __init__(self, mjcf_path: str | Path, *, worlds: int = 512, width: int = 128, height: int = 128):
        try:
            import mujoco
            import mujoco_warp as mjw
        except ImportError as exc:
            raise RuntimeError("install mujoco-warp and warp-lang for the A100 renderer") from exc
        self._mujoco = mujoco
        self._mjw = mjw
        self.model_host = mujoco.MjModel.from_xml_path(str(mjcf_path))
        self.worlds = worlds
        self.width = width
        self.height = height
        # Model metadata is shared across worlds. `make_data` allocates the
        # batched dynamic state, so no model field needs a custom batch size.
        self.model = mjw.put_model(self.model_host)
        self.data = mjw.make_data(self.model_host, nworld=worlds)
        self.context = mjw.create_render_context(
            self.model_host,
            nworld=worlds,
            cam_res=(width, height),
            render_rgb=False,
            render_depth=True,
            render_seg=True,
            use_textures=False,
        )

    def render(self, repeats: int = 1) -> WarpRenderResult:
        start = time.perf_counter()
        for _ in range(max(1, repeats)):
            self._mjw.render(self.model, self.data, self.context)
        # Synchronising through numpy gives a meaningful wall-clock benchmark.
        depth = self.context.depth_data.numpy().reshape(self.worlds, self.height, self.width).copy()
        segmentation = self.context.seg_data.numpy().reshape(self.worlds, self.height, self.width, 2).copy()
        elapsed = time.perf_counter() - start
        return WarpRenderResult(depth, segmentation, elapsed / max(1, repeats))

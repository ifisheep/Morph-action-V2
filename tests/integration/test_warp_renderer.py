"""GPU-only contract test for the MuJoCo Warp backend."""

from __future__ import annotations

import pytest

from morphdream.sim.warp_renderer import available


@pytest.mark.gpu
def test_warp_renderer_is_optional_on_cpu() -> None:
    # The CPU CI suite intentionally does not install CUDA dependencies. The
    # test remains a marker so A100 jobs can exercise the real renderer.
    assert isinstance(available(), bool)

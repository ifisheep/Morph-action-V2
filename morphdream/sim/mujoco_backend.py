"""Optional MuJoCo runtime boundary for exported MJCF scenes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class MuJoCoRuntime:
    model: object
    data: object

    @classmethod
    def from_mjcf(cls, path: str | Path) -> "MuJoCoRuntime":
        try:
            import mujoco
        except ImportError as exc:
            raise RuntimeError("install the optional 'sim' extra to load MuJoCo scenes") from exc
        model = mujoco.MjModel.from_xml_path(str(path))
        return cls(model, mujoco.MjData(model))

    def step(self, steps: int = 1) -> None:
        import mujoco

        for _ in range(max(0, steps)):
            mujoco.mj_step(self.model, self.data)

    @property
    def time_s(self) -> float:
        return float(self.data.time)


def available() -> bool:
    try:
        import mujoco  # noqa: F401
    except ImportError:
        return False
    return True

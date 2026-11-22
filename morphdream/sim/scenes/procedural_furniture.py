"""Small deterministic furniture generator used when MolmoSpaces is unavailable."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class Furniture:
    object_id: int
    category: str
    center_xyz: tuple[float, float, float]
    size_xyz: tuple[float, float, float]
    color_rgb: tuple[int, int, int] = (160, 160, 160)

    @property
    def min_xyz(self) -> np.ndarray:
        return np.asarray(self.center_xyz) - np.asarray(self.size_xyz) / 2

    @property
    def max_xyz(self) -> np.ndarray:
        return np.asarray(self.center_xyz) + np.asarray(self.size_xyz) / 2


@dataclass
class ProceduralScene:
    scene_id: str
    objects: list[Furniture] = field(default_factory=list)
    target_object_id: int | None = None
    hiding_type: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def save(self, path: str | Path) -> None:
        payload = asdict(self)
        Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> ProceduralScene:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        data["objects"] = [Furniture(**item) for item in data.get("objects", [])]
        return cls(**data)


def make_demo_scene(scene_id: str = "demo-000") -> ProceduralScene:
    return ProceduralScene(
        scene_id,
        objects=[
            Furniture(1, "bed", (0.0, 0.0, 0.45), (2.0, 1.4, 0.7)),
            Furniture(2, "sofa", (2.5, 0.8, 0.45), (1.6, 0.8, 0.7)),
            Furniture(3, "shelf", (-2.0, -1.2, 1.0), (0.8, 0.4, 2.0)),
            Furniture(4, "target", (0.2, 0.0, 0.16), (0.18, 0.18, 0.18), (220, 60, 60)),
        ],
        target_object_id=4,
    )

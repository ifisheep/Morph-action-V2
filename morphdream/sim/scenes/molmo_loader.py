"""Loader boundary for exported MolmoSpaces scenes.

The loader accepts standalone MJCF files and the JSON scene format emitted by
the procedural fallback. It deliberately keeps scene metadata independent of
the optional MuJoCo package so Mac CPU tests remain lightweight.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from .procedural_furniture import Furniture, ProceduralScene


@dataclass(frozen=True)
class MolmoScene:
    scene_id: str
    path: str
    source: str = "molmospaces"
    metadata: dict[str, str] = field(default_factory=dict)
    objects: tuple[Furniture, ...] = ()


def load_scene(path: str | Path) -> MolmoScene | ProceduralScene:
    path = Path(path)
    if path.suffix.lower() == ".json":
        return ProceduralScene.load(path)
    if path.suffix.lower() not in {".xml", ".mjcf"}:
        raise ValueError(f"unsupported scene format: {path.suffix}")
    root = ET.parse(path).getroot()
    scene_id = root.attrib.get("name", path.stem)
    objects: list[Furniture] = []
    for index, body in enumerate(root.findall(".//body"), start=1):
        name = body.attrib.get("name", f"body-{index}")
        pos = tuple(float(v) for v in body.attrib.get("pos", "0 0 0").split())
        if len(pos) != 3:
            continue
        geom = body.find("geom")
        if geom is None:
            continue
        size_values = tuple(float(v) for v in geom.attrib.get("size", "0.1 0.1 0.1").split())
        size = tuple(2 * v for v in size_values[:3]) if len(size_values) >= 3 else (0.2, 0.2, 0.2)
        objects.append(Furniture(index, name, pos, size))
    return MolmoScene(scene_id, str(path), objects=tuple(objects))


def discover_scenes(root: str | Path, limit: int | None = None) -> list[Path]:
    paths = sorted(Path(root).rglob("*.xml")) + sorted(Path(root).rglob("*.json"))
    return paths if limit is None else paths[:limit]

"""Morphology joint-lock descriptions and MuJoCo XML patching."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class JointLock:
    joint: str
    angle_rad: float = 0.0
    role: str = "support"


@dataclass(frozen=True)
class Morphology:
    morph_id: str
    locks: tuple[JointLock, ...] = ()
    contact_roles: Mapping[str, str] = field(default_factory=dict)


def load_morphology(path: str | Path) -> Morphology:
    """Load a small YAML morphology file without requiring PyYAML at runtime."""
    text = Path(path).read_text(encoding="utf-8")
    morph_id = Path(path).stem
    locks: list[JointLock] = []
    roles: dict[str, str] = {}
    section = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith(":"):
            section = line[:-1]
            continue
        if line.startswith("morph_id:"):
            morph_id = line.split(":", 1)[1].strip().strip('"\'')
        elif section == "locks" and line.startswith("-"):
            values = dict(re.findall(r"(joint|angle_rad|role):\s*([^,}]+)", line))
            if values:
                locks.append(JointLock(values.get("joint", ""), float(values.get("angle_rad", 0)), values.get("role", "support")))
        elif section == "contact_roles" and ":" in line:
            key, value = line.split(":", 1)
            roles[key.strip()] = value.strip().strip('"\'')
    return Morphology(morph_id, tuple(lock for lock in locks if lock.joint), roles)


def apply_locks(joints: Mapping[str, float], locks: tuple[JointLock, ...] | list[JointLock]) -> dict[str, float]:
    result = dict(joints)
    for lock in locks:
        if lock.joint in result:
            result[lock.joint] = float(lock.angle_rad)
    return result

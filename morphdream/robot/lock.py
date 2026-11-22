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
    lock_mask: Mapping[str, bool] = field(default_factory=dict)
    lock_angles: Mapping[str, float] = field(default_factory=dict)
    support_segments: tuple[int, ...] = ()
    camera_height_target_m: float = 0.30


def load_morphology(path: str | Path) -> Morphology:
    """Load a small YAML morphology file without requiring PyYAML at runtime."""
    text = Path(path).read_text(encoding="utf-8")
    try:
        import yaml

        payload = yaml.safe_load(text) or {}
        locks = tuple(
            JointLock(str(item["joint"]), float(item.get("angle_rad", 0.0)), str(item.get("role", "support")))
            for item in payload.get("locks", [])
            if isinstance(item, dict) and "joint" in item
        )
        return Morphology(
            str(payload.get("morph_id", Path(path).stem)),
            locks,
            {str(key): str(value) for key, value in payload.get("contact_roles", {}).items()},
            {str(key): bool(value) for key, value in payload.get("lock_mask", {}).items()},
            {str(key): float(value) for key, value in payload.get("lock_angles", {}).items()},
            tuple(int(value) for value in payload.get("support_segments", [])),
            float(payload.get("camera_height_target_m", 0.30)),
        )
    except ImportError:
        pass
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
    return Morphology(morph_id, tuple(lock for lock in locks if lock.joint), contact_roles=roles)


def apply_locks(joints: Mapping[str, float], locks: tuple[JointLock, ...] | list[JointLock]) -> dict[str, float]:
    result = dict(joints)
    for lock in locks:
        if lock.joint in result:
            result[lock.joint] = float(lock.angle_rad)
    return result

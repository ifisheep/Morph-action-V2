"""Shared data contracts for every MorphDream module.

The classes in this module intentionally contain no simulator imports. They are
small, serialisable contracts that make it possible to run the reasoning and
imagination stack from recorded observations on a CPU machine.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Literal, Protocol

import numpy as np


def _array(value: Any, *, dtype: Any = float) -> np.ndarray:
    return np.asarray(value, dtype=dtype)


@dataclass(frozen=True)
class Pose:
    position: np.ndarray
    quaternion: np.ndarray = field(default_factory=lambda: np.array([1.0, 0.0, 0.0, 0.0]))

    def __post_init__(self) -> None:
        position = _array(self.position).reshape(-1)
        quat = _array(self.quaternion).reshape(-1)
        if position.shape != (3,):
            raise ValueError("Pose.position must have shape (3,)")
        if quat.shape != (4,):
            raise ValueError("Pose.quaternion must have shape (4,) in (w,x,y,z) order")
        norm = float(np.linalg.norm(quat))
        if norm == 0:
            raise ValueError("Pose quaternion cannot be zero")
        object.__setattr__(self, "position", position.copy())
        object.__setattr__(self, "quaternion", (quat / norm).copy())

    @classmethod
    def identity(cls) -> Pose:
        return cls(np.zeros(3), np.array([1.0, 0.0, 0.0, 0.0]))


@dataclass(frozen=True)
class Pose2D:
    x: float
    y: float
    yaw: float = 0.0


@dataclass(frozen=True)
class RegionRef:
    region_id: str
    center_xyz: np.ndarray
    size_xyz: np.ndarray = field(default_factory=lambda: np.ones(3))

    def __post_init__(self) -> None:
        center = _array(self.center_xyz).reshape(-1)
        size = _array(self.size_xyz).reshape(-1)
        if center.shape != (3,) or size.shape != (3,):
            raise ValueError("RegionRef vectors must have shape (3,)")
        if np.any(size <= 0):
            raise ValueError("RegionRef.size_xyz must be positive")
        object.__setattr__(self, "center_xyz", center.copy())
        object.__setattr__(self, "size_xyz", size.copy())


AttentionKind = Literal["crop", "zoom", "revisit"]


@dataclass(frozen=True)
class AttentionOp:
    kind: AttentionKind
    region_id: str | None = None
    scale: float = 1.0

    def __post_init__(self) -> None:
        if self.kind in {"crop", "zoom"} and self.scale <= 0:
            raise ValueError("attention scale must be positive")


@dataclass(frozen=True)
class VoxelGrid:
    """A dense voxel grid with values 0 free, 1 occupied and -1 unknown."""

    values: np.ndarray
    origin_xyz: np.ndarray
    voxel_size_m: float

    def __post_init__(self) -> None:
        values = np.asarray(self.values, dtype=np.int8)
        origin = _array(self.origin_xyz).reshape(-1)
        if values.ndim != 3:
            raise ValueError("VoxelGrid.values must be a 3-D array")
        if origin.shape != (3,):
            raise ValueError("VoxelGrid.origin_xyz must have shape (3,)")
        if self.voxel_size_m <= 0:
            raise ValueError("voxel_size_m must be positive")
        if not np.all(np.isin(values, (-1, 0, 1))):
            raise ValueError("VoxelGrid values must be -1, 0 or 1")
        object.__setattr__(self, "values", values.copy())
        object.__setattr__(self, "origin_xyz", origin.copy())

    @property
    def shape(self) -> tuple[int, int, int]:
        return tuple(int(v) for v in self.values.shape)

    def world_to_index(self, point_xyz: Sequence[float]) -> tuple[int, int, int] | None:
        index = np.floor((np.asarray(point_xyz) - self.origin_xyz) / self.voxel_size_m).astype(int)
        if np.any(index < 0) or np.any(index >= np.asarray(self.values.shape)):
            return None
        return tuple(int(v) for v in index)

    def at(self, point_xyz: Sequence[float], default: int = -1) -> int:
        index = self.world_to_index(point_xyz)
        return default if index is None else int(self.values[index])


@dataclass(frozen=True)
class SemanticGrid:
    labels: np.ndarray
    class_names: Mapping[int, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        labels = np.asarray(self.labels, dtype=np.int32)
        if labels.ndim != 3:
            raise ValueError("SemanticGrid.labels must be a 3-D array")
        object.__setattr__(self, "labels", labels.copy())
        object.__setattr__(self, "class_names", dict(self.class_names))


@dataclass(frozen=True)
class HypothesisSet:
    probabilities: Mapping[str, float]

    def __post_init__(self) -> None:
        values = {str(k): float(v) for k, v in self.probabilities.items()}
        if any(v < 0 for v in values.values()):
            raise ValueError("hypothesis probabilities must be non-negative")
        total = sum(values.values())
        if values and total <= 0:
            raise ValueError("hypothesis probabilities must have positive mass")
        object.__setattr__(self, "probabilities", {k: v / total for k, v in values.items()} if total else {})

    def update(self, likelihoods: Mapping[str, float]) -> HypothesisSet:
        posterior = {
            key: self.probabilities.get(key, 0.0) * max(float(value), 0.0)
            for key, value in likelihoods.items()
        }
        if not posterior:
            return self
        if sum(posterior.values()) == 0:
            posterior = dict(self.probabilities)
        return HypothesisSet(posterior)

    @property
    def most_likely(self) -> tuple[str, float] | None:
        return max(self.probabilities.items(), key=lambda item: item[1], default=None)


@dataclass(frozen=True)
class ObjectRecord:
    object_id: int | str
    category: str
    center_xyz: np.ndarray
    size_xyz: np.ndarray
    confidence: float = 1.0

    def __post_init__(self) -> None:
        center = _array(self.center_xyz).reshape(-1)
        size = _array(self.size_xyz).reshape(-1)
        if center.shape != (3,) or size.shape != (3,) or np.any(size <= 0):
            raise ValueError("ObjectRecord geometry must be positive 3-vectors")
        if not 0 <= self.confidence <= 1:
            raise ValueError("ObjectRecord.confidence must be in [0, 1]")
        object.__setattr__(self, "center_xyz", center.copy())
        object.__setattr__(self, "size_xyz", size.copy())


@dataclass(frozen=True)
class TransitionStat:
    mean_time_s: float
    std_time_s: float
    success_rate: float
    n_trials: int


@dataclass(frozen=True)
class JitterModel:
    coeffs: tuple[float, ...]
    stable_phase: tuple[float, float] | None = None


@dataclass(frozen=True)
class Resume:
    morph_id: str
    camera_height_range_m: tuple[float, float]
    camera_pitch_range_rad: tuple[float, float]
    camera_yaw_range_rad: tuple[float, float]
    reachable_camera_poses: np.ndarray
    min_clearance_height_m: float
    min_width_m: float
    speed_mps: Mapping[str, float]
    jitter: Mapping[str, JitterModel]
    gaze_decoupled: bool
    self_occlusion_mask: np.ndarray
    transitions: Mapping[str, TransitionStat]
    energy_per_s: float
    fall_rate_per_min: float
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        poses = np.asarray(self.reachable_camera_poses, dtype=float)
        mask = np.asarray(self.self_occlusion_mask, dtype=bool)
        if poses.ndim != 2 or poses.shape[1] != 7:
            raise ValueError("reachable_camera_poses must have shape (N, 7)")
        if self.min_clearance_height_m < 0 or self.min_width_m < 0:
            raise ValueError("resume clearance and width cannot be negative")
        object.__setattr__(self, "reachable_camera_poses", poses.copy())
        object.__setattr__(self, "self_occlusion_mask", mask.copy())
        object.__setattr__(self, "speed_mps", dict(self.speed_mps))
        object.__setattr__(self, "jitter", dict(self.jitter))
        object.__setattr__(self, "transitions", dict(self.transitions))
        object.__setattr__(self, "provenance", dict(self.provenance))


@dataclass
class Observation:
    t: float
    morph_id: str
    depth: np.ndarray
    seg: np.ndarray
    seg_classes: dict[int, str]
    rgb: np.ndarray | None
    K: np.ndarray
    T_world_cam: np.ndarray
    source: Literal["real_render"] = "real_render"

    def __post_init__(self) -> None:
        self.depth = np.asarray(self.depth, dtype=float)
        self.seg = np.asarray(self.seg, dtype=np.int32)
        self.K = np.asarray(self.K, dtype=float)
        self.T_world_cam = np.asarray(self.T_world_cam, dtype=float)
        if self.depth.ndim != 2 or self.seg.shape != self.depth.shape:
            raise ValueError("depth and seg must be 2-D arrays with matching shape")
        if self.K.shape != (3, 3) or self.T_world_cam.shape != (4, 4):
            raise ValueError("K must be 3x3 and T_world_cam must be 4x4")
        if self.source != "real_render":
            raise ValueError("only real_render observations can enter SceneMemory")


@dataclass(frozen=True)
class MemorySnapshot:
    occupancy: VoxelGrid
    semantics: SemanticGrid
    hypotheses: HypothesisSet
    objects: tuple[ObjectRecord, ...] = ()
    content_hash: str = ""

    def __post_init__(self) -> None:
        objects = tuple(self.objects)
        object.__setattr__(self, "objects", objects)
        if not self.content_hash:
            digest = sha256()
            digest.update(self.occupancy.values.tobytes())
            digest.update(self.semantics.labels.tobytes())
            digest.update(repr(sorted(self.hypotheses.probabilities.items())).encode())
            for obj in objects:
                digest.update(str(obj.object_id).encode())
                digest.update(obj.category.encode())
                digest.update(obj.center_xyz.tobytes())
                digest.update(obj.size_xyz.tobytes())
                digest.update(repr(obj.confidence).encode())
            object.__setattr__(self, "content_hash", digest.hexdigest())


@dataclass(frozen=True)
class RobotState:
    morph_id: str
    pose: Pose = field(default_factory=Pose.identity)
    velocity_mps: float = 0.0
    fell: bool = False


ActionLevel = Literal["view", "attention", "morph"]
BottleneckKind = Literal["occlusion", "fov", "scale", "angle", "quality", "reachability"]


@dataclass(frozen=True)
class Bottleneck:
    kind: BottleneckKind
    region: RegionRef
    remedy_viewpoints: tuple[Pose, ...] = ()
    reachable_by: Mapping[str, bool] = field(default_factory=dict)
    details: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ActionCandidate:
    level: ActionLevel
    morph_id: str
    viewpoint: Pose | None = None
    attention: AttentionOp | None = None
    rationale: str = ""
    target_region_id: str | None = None


@dataclass(frozen=True)
class Score:
    gain: float
    gain_lcb: float
    cost_s: float
    risk: float
    tier_used: int
    details: Mapping[str, Any] = field(default_factory=dict)

    @property
    def utility(self) -> float:
        return self.gain_lcb / max(self.cost_s, 1e-6) - self.risk


@dataclass(frozen=True)
class SkillResult:
    success: bool
    duration_s: float
    fell: bool
    observations: tuple[Observation, ...] = ()
    details: Mapping[str, Any] = field(default_factory=dict)


class Evaluator(Protocol):
    def score(
        self,
        mem: MemorySnapshot,
        cand: ActionCandidate,
        resumes: Mapping[str, Resume],
        state: RobotState,
    ) -> Score: ...


class Body(Protocol):
    def transition_to(self, morph_id: str) -> SkillResult: ...
    def move_to(self, pose2d: Pose2D, speed: float) -> SkillResult: ...
    def look_at(self, target_xyz: np.ndarray, stabilize: bool = True) -> SkillResult: ...
    def scan(self, yaw_range: tuple[float, float], pitch_range: tuple[float, float]) -> SkillResult: ...
    def pause(self, seconds: float) -> SkillResult: ...


def dataclass_to_jsonable(value: Any) -> Any:
    """Convert nested contracts to JSON-safe values for logs."""
    if isinstance(value, np.ndarray):
        return value.tolist()
    if hasattr(value, "__dataclass_fields__"):
        return {key: dataclass_to_jsonable(getattr(value, key)) for key in value.__dataclass_fields__}
    if isinstance(value, Mapping):
        return {str(key): dataclass_to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [dataclass_to_jsonable(item) for item in value]
    return value

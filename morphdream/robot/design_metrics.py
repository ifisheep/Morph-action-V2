"""Static design metrics for superset-robot candidates (task R3).

Every function works on one MuJoCo model built from
``morphdream.robot.assembly.build_mjcf``. Nothing here tunes gaits or
controllers: each morphology is placed in its template pose, held by the
position servos, and measured once it settles.

Measurement rules
-----------------
* A posture counts only if it is reached: every targeted joint within
  ``POSTURE_TOLERANCE_RAD``, the rear body (spine 2-3) within
  ``TILT_TOLERANCE_RAD`` of level, and, for legged templates, the head and
  neck off the floor (a robot leaning on its head has not reached the pose).
  Metrics of unreached postures are reported but flagged.
* Required joint torque is read from a copy of the model whose servos have no
  force limit, after it settles in the template pose. That is the torque the
  pose needs; it is then compared with the derated servo limit.
* The support polygon comes from actual floor contacts, not from assumed feet.
* Camera reach comes from a neck-pitch sweep of the settled robot, so camera
  height and camera tilt stay coupled as they are on the hardware.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Any, Mapping

import mujoco
import numpy as np

from morphdream.robot.assembly import AssemblySpec, build_mjcf

POSTURE_TOLERANCE_RAD = 0.05
TILT_TOLERANCE_RAD = math.radians(10.0)
SETTLE_SECONDS = 2.0
LEVEL_GAZE_TOLERANCE_RAD = math.radians(15.0)
FLOOR_Z = -0.02
LEG_PAIRS = 3
RETRACT_GRID_RAD = np.radians(np.arange(-135.0, 135.1, 15.0))


# ---------------------------------------------------------------- utilities


def _joint_id(model, name: str) -> int:
    return mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, name)


def _qadr(model, name: str) -> int | None:
    joint = _joint_id(model, name)
    return None if joint < 0 else int(model.jnt_qposadr[joint])


def _floor_id(model) -> int:
    return mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "floor")


def self_contacts(model, data) -> list[tuple[str, str]]:
    floor = _floor_id(model)
    pairs = []
    for contact in data.contact[: data.ncon]:
        if floor in (contact.geom1, contact.geom2):
            continue
        pairs.append((
            mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, contact.geom1),
            mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, contact.geom2),
        ))
    return pairs


def rear_frame(model, data) -> tuple[np.ndarray, np.ndarray]:
    """Unit vectors (rear, up) of the rear body, which every template keeps on the ground.

    ``rear`` points from spine 2 to spine 3. ``up`` is opposite to where the
    rearmost legs hang, orthogonalised against ``rear``.
    """
    body = lambda name: mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, name)  # noqa: E731
    rear = data.xpos[body("spine_3")] - data.xpos[body("spine_2")]
    rear = rear / np.linalg.norm(rear)
    hang = data.xmat[body("spine_3")].reshape(3, 3) @ np.array([0.0, 0.0, -1.0])
    up = -(hang - (hang @ rear) * rear)
    return rear, up / np.linalg.norm(up)


def apply_joint_targets(model, data, targets: Mapping[str, float]) -> None:
    for name, angle in targets.items():
        adr = _qadr(model, name)
        if adr is not None:
            data.qpos[adr] = angle


def _set_ctrl(model, data, targets: Mapping[str, float]) -> None:
    data.ctrl[:] = 0.0
    for index in range(model.nu):
        joint = model.actuator_trnid[index, 0]
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, joint)
        data.ctrl[index] = targets.get(name, 0.0)


def _geom_extent_z(model, data, geom: int) -> float:
    """Half-extent of a geom along world z."""
    kind = model.geom_type[geom]
    rotation = data.geom_xmat[geom].reshape(3, 3)
    size = model.geom_size[geom]
    if kind == mujoco.mjtGeom.mjGEOM_SPHERE:
        return float(size[0])
    if kind == mujoco.mjtGeom.mjGEOM_CAPSULE:
        return float(abs(rotation[2, 2]) * size[1] + size[0])
    if kind == mujoco.mjtGeom.mjGEOM_BOX:
        return float(np.abs(rotation[2, :]) @ size[:3])
    return float(model.geom_rbound[geom])


def _colliding_geoms(model) -> list[int]:
    floor = _floor_id(model)
    return [
        geom for geom in range(model.ngeom)
        if geom != floor and not (model.geom_contype[geom] == 0 and model.geom_conaffinity[geom] == 0)
    ]


def lowest_point_z(model, data) -> float:
    """Lowest point of any colliding geometry (floor excluded)."""
    return min(float(data.geom_xpos[g][2]) - _geom_extent_z(model, data, g) for g in _colliding_geoms(model))


def highest_point_z(model, data) -> float:
    """Highest point of any colliding geometry (floor excluded)."""
    return max(float(data.geom_xpos[g][2]) + _geom_extent_z(model, data, g) for g in _colliding_geoms(model))


# --------------------------------------------------------------- posture


def upright_segment_targets(upright_segments: list[int] | tuple[int, ...]) -> dict[str, float]:
    """Spine pitch targets that stand segments ``0..k`` up as one column.

    Segments ahead of the bend stay collinear (pitch 0); the joint behind the
    last upright segment bends by -90 degrees (see assembly sign conventions).
    """
    if not upright_segments:
        return {}
    top = max(upright_segments)
    if sorted(upright_segments) != list(range(top + 1)):
        raise ValueError("upright segments must be a contiguous run starting at segment 0")
    targets = {f"spine_{k}_pitch": 0.0 for k in range(top)}
    targets[f"spine_{top}_pitch"] = -math.pi / 2
    return targets


def base_targets(template: Any, overrides: Mapping[str, float] | None = None) -> dict[str, float]:
    """Spine, neck and support-leg targets of a template (non-support legs not yet set)."""
    targets = {name: float(angle) for name, angle in template.lock_angles.items()}
    targets.update(overrides or {})
    targets["neck_pitch"] = float(template.gaze_nominal_pitch_rad)
    for pair in range(LEG_PAIRS):
        for side in ("left", "right"):
            if template.contact_roles.get(f"leg_{side}_{pair}", "retracted") == "support":
                for joint in (f"hip_yaw_{side}_{pair}", f"hip_pitch_{side}_{pair}", f"knee_{side}_{pair}"):
                    targets[joint] = 0.0
    return targets


def retracted_legs(template: Any) -> list[tuple[str, int]]:
    return [
        (side, pair)
        for pair in range(LEG_PAIRS)
        for side in ("left", "right")
        if template.contact_roles.get(f"leg_{side}_{pair}", "retracted") != "support"
    ]


LEG_GROUND_ALLOWANCE_M = 0.01  # a folded leg may reach this far below its hip (spine bottom)


def _extent_along(model, data, geom: int, axis: np.ndarray) -> float:
    kind = model.geom_type[geom]
    rotation = data.geom_xmat[geom].reshape(3, 3)
    size = model.geom_size[geom]
    if kind == mujoco.mjtGeom.mjGEOM_SPHERE:
        return float(size[0])
    if kind == mujoco.mjtGeom.mjGEOM_CAPSULE:
        return float(abs(rotation[:, 2] @ axis) * size[1] + size[0])
    if kind == mujoco.mjtGeom.mjGEOM_BOX:
        return float(np.abs(rotation.T @ axis) @ size[:3])
    return float(model.geom_rbound[geom])


def find_retraction_pose(model, targets: Mapping[str, float], side: str, pair: int) -> tuple[float, float, float] | None:
    """Collision-free (hip_yaw, hip_pitch, knee) that folds this leg flat against the body.

    The search is kinematic on a lifted robot with every other joint at
    ``targets``. Hip yaw stays at zero so left and right legs fold alike.
    Along the rear body's up axis and relative to the hip, the folded leg must
    not reach more than ``LEG_GROUND_ALLOWANCE_M`` below the hip (so it never
    becomes a foot). Among such poses the most compact fold wins (smallest
    reach from the hip), then the flattest (lowest highest point), then the
    one folded furthest toward the rear, which keeps the centre of mass back
    behind the front-mounted head. Returns ``None`` when no grid pose is free
    of self-contact.
    """
    data = mujoco.MjData(model)
    data.qpos[2] = 1.5
    data.qpos[3] = 1.0
    apply_joint_targets(model, data, targets)
    prefix = f"leg_{side}_{pair}"
    hip_body = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, prefix)
    geoms = [mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, name) for name in (f"{prefix}_upper", f"{prefix}_shin", f"foot_{side}_{pair}")]
    names = (f"hip_yaw_{side}_{pair}", f"hip_pitch_{side}_{pair}", f"knee_{side}_{pair}")
    adrs = [_qadr(model, name) for name in names]
    if any(adr is None for adr in adrs) or hip_body < 0 or min(geoms) < 0:
        return None
    feasible: list[tuple[float, float, float, float, tuple[float, float, float]]] = []
    fallback: list[tuple[float, float, float, float, tuple[float, float, float]]] = []
    for hip_pitch in RETRACT_GRID_RAD:
        for knee in RETRACT_GRID_RAD:
            data.qpos[adrs[0]] = 0.0
            data.qpos[adrs[1]] = hip_pitch
            data.qpos[adrs[2]] = knee
            mujoco.mj_forward(model, data)
            if self_contacts(model, data):
                continue
            rear, up = rear_frame(model, data)
            hip = data.xpos[hip_body]
            reach = max(float(np.linalg.norm(data.geom_xpos[g] - hip)) + float(model.geom_size[g][0]) for g in geoms)
            toward_rear = float((data.geom_xpos[geoms[2]] - hip) @ rear)
            top = max(float((data.geom_xpos[g] - hip) @ up) + _extent_along(model, data, g, up) for g in geoms)
            bottom = min(float((data.geom_xpos[g] - hip) @ up) - _extent_along(model, data, g, up) for g in geoms)
            effort = abs(float(hip_pitch)) + abs(float(knee))
            pose = (0.0, float(hip_pitch), float(knee))
            if bottom >= -LEG_GROUND_ALLOWANCE_M:
                feasible.append((round(reach, 3), round(top, 3), -round(toward_rear, 3), effort, pose))
            else:
                fallback.append((-round(bottom, 3), round(reach, 3), 0.0, effort, pose))
    if feasible:
        return min(feasible)[-1]
    if fallback:
        return min(fallback)[-1]
    return None


def full_targets(model, template: Any, overrides: Mapping[str, float] | None = None) -> tuple[dict[str, float], dict[str, Any]]:
    """Template targets with a searched retraction pose for every non-support leg."""
    targets = base_targets(template, overrides)
    legs = retracted_legs(template)
    # Fold every non-support leg first with a neutral guess, then refine each
    # leg against the others so neighbours are taken into account.
    for side, pair in legs:
        targets.update({f"hip_yaw_{side}_{pair}": 0.0, f"hip_pitch_{side}_{pair}": 0.0, f"knee_{side}_{pair}": 0.0})
    poses: dict[str, Any] = {}
    for _ in range(2):
        for side, pair in legs:
            pose = find_retraction_pose(model, targets, side, pair)
            poses[f"leg_{side}_{pair}"] = None if pose is None else [round(math.degrees(v), 1) for v in pose]
            if pose is not None:
                targets.update(dict(zip((f"hip_yaw_{side}_{pair}", f"hip_pitch_{side}_{pair}", f"knee_{side}_{pair}"), pose)))
    return targets, poses


def place_on_floor(model, data, targets: Mapping[str, float], clearance: float = 0.003) -> None:
    """Pose the robot kinematically with the rear body level and just above the floor."""
    mujoco.mj_resetData(model, data)
    data.qpos[3] = 1.0
    apply_joint_targets(model, data, targets)
    mujoco.mj_forward(model, data)
    rear, up = rear_frame(model, data)
    side = np.cross(up, rear)
    current = np.column_stack([rear, side, up])
    desired = np.column_stack([[-1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]])
    rotation = desired @ current.T
    quat = np.zeros(4)
    mujoco.mju_mat2Quat(quat, rotation.reshape(-1))
    data.qpos[3:7] = quat
    mujoco.mj_forward(model, data)
    data.qpos[2] += FLOOR_Z + clearance - lowest_point_z(model, data)
    mujoco.mj_forward(model, data)


def settle(model, data, targets: Mapping[str, float], seconds: float = SETTLE_SECONDS) -> None:
    _set_ctrl(model, data, targets)
    for _ in range(int(round(seconds / model.opt.timestep))):
        mujoco.mj_step(model, data)
    mujoco.mj_forward(model, data)


def posture_error(model, data, targets: Mapping[str, float]) -> tuple[float, str]:
    worst, worst_name = 0.0, ""
    for name, angle in targets.items():
        adr = _qadr(model, name)
        if adr is None:
            continue
        error = abs(float(data.qpos[adr]) - angle)
        if error > worst:
            worst, worst_name = error, name
    return worst, worst_name


def rear_tilt(model, data) -> float:
    _, up = rear_frame(model, data)
    return float(math.acos(max(-1.0, min(1.0, float(up[2])))))


# ------------------------------------------------------------ statics


def _hull(points: np.ndarray) -> list[np.ndarray]:
    pts = sorted({(round(float(x), 6), round(float(y), 6)) for x, y in points})
    if len(pts) < 3:
        return [np.asarray(p) for p in pts]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list[tuple[float, float]] = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper: list[tuple[float, float]] = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return [np.asarray(p) for p in lower[:-1] + upper[:-1]]


def polygon_margin(point: np.ndarray, points: np.ndarray, min_area_m2: float = 1e-4) -> float | None:
    """Signed distance from ``point`` to the convex hull of ``points`` (positive inside).

    Returns ``None`` when the hull is degenerate (fewer than three points or
    area below ``min_area_m2``), for example a body lying on a line contact.
    """
    hull = _hull(np.asarray(points, dtype=float).reshape(-1, 2))
    if len(hull) < 3:
        return None
    area = 0.5 * abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(hull, hull[1:] + hull[:1])))
    if area < min_area_m2:
        return None
    distances = []
    for a, b in zip(hull, hull[1:] + hull[:1]):
        edge = b - a
        rel = np.asarray(point) - a
        distances.append((edge[0] * rel[1] - edge[1] * rel[0]) / max(float(np.linalg.norm(edge)), 1e-9))
    return float(min(distances))


def floor_contact_points(model, data) -> np.ndarray:
    floor = _floor_id(model)
    points = [contact.pos[:2].copy() for contact in data.contact[: data.ncon] if floor in (contact.geom1, contact.geom2)]
    return np.asarray(points).reshape(-1, 2)


def static_margin(model, data) -> tuple[float | None, int]:
    points = floor_contact_points(model, data)
    com = data.subtree_com[1, :2]
    return polygon_margin(com, points), int(len(points))


def joint_torques(model, data) -> dict[str, float]:
    torques = {}
    for index in range(model.nu):
        joint = model.actuator_trnid[index, 0]
        torques[mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, joint)] = abs(float(data.actuator_force[index]))
    return torques


# --------------------------------------------------------------- camera


@dataclass(frozen=True)
class GazeSample:
    neck_pitch_rad: float
    height_m: float  # above the floor surface
    elevation_rad: float
    self_contact: bool
    floor_collision: bool = False  # head or neck pushed into the floor

    @property
    def usable(self) -> bool:
        return not self.self_contact and not self.floor_collision and self.height_m > 0.0


HEAD_FLOOR_PENETRATION_M = 0.01  # deeper than soft-contact sag means the head is in the floor


def _head_in_floor(model, data, depth: float = HEAD_FLOOR_PENETRATION_M) -> bool:
    """True if the head or neck touches the floor deeper than ``depth``."""
    floor = _floor_id(model)
    moving = {mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, name) for name in ("head_geom", "neck_link")}
    for contact in data.contact[: data.ncon]:
        pair = {contact.geom1, contact.geom2}
        if floor in pair and pair & moving and contact.dist < -depth:
            return True
    return False


def gaze_sweep(model, data, template: Any, samples: int = 31) -> list[GazeSample]:
    """Neck-pitch sweep over the template's gaze range from the settled pose (kinematic)."""
    qpos = data.qpos.copy()
    adr = _qadr(model, "neck_pitch")
    camera = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_CAMERA, "depth_camera")
    low, high = template.gaze_pitch_range_rad
    result = []
    for pitch in np.linspace(low, high, samples):
        data.qpos[:] = qpos
        if adr is not None:
            data.qpos[adr] = pitch
        mujoco.mj_forward(model, data)
        axis = -data.cam_xmat[camera].reshape(3, 3)[:, 2]
        elevation = math.atan2(float(axis[2]), float(np.linalg.norm(axis[:2])))
        height = float(data.cam_xpos[camera][2]) - FLOOR_Z
        result.append(GazeSample(float(pitch), height, elevation, bool(self_contacts(model, data)), _head_in_floor(model, data)))
    data.qpos[:] = qpos
    mujoco.mj_forward(model, data)
    return result


def camera_summary(sweep: list[GazeSample]) -> dict[str, Any]:
    usable = [s for s in sweep if s.usable]
    level = [s for s in usable if abs(s.elevation_rad) <= LEVEL_GAZE_TOLERANCE_RAD]
    nearest = min(usable, key=lambda s: abs(s.elevation_rad)) if usable else None
    return {
        "level_gaze_height_m": None if nearest is None else round(nearest.height_m, 4),
        "level_gaze_elevation_deg": None if nearest is None else round(math.degrees(nearest.elevation_rad), 1),
        "near_level_height_range_m": None if not level else [round(min(s.height_m for s in level), 4), round(max(s.height_m for s in level), 4)],
        "sweep_height_range_m": None if not usable else [round(min(s.height_m for s in usable), 4), round(max(s.height_m for s in usable), 4)],
        "sweep_elevation_range_deg": None if not usable else [round(math.degrees(min(s.elevation_rad for s in usable)), 1), round(math.degrees(max(s.elevation_rad for s in usable)), 1)],
        "self_contact_samples": sum(s.self_contact for s in sweep),
        "floor_collision_samples": sum(s.floor_collision for s in sweep),
    }


# ------------------------------------------------------------- one pose


def measure_morphology(
    spec: AssemblySpec,
    template: Any,
    *,
    overrides: Mapping[str, float] | None = None,
    static_derating: float = 0.5,
    settle_seconds: float = SETTLE_SECONDS,
) -> dict[str, Any]:
    """Place, settle and measure one morphology on one candidate."""
    limited = mujoco.MjModel.from_xml_string(build_mjcf(spec))
    unlimited = mujoco.MjModel.from_xml_string(build_mjcf(replace(spec, actuator_torque_limit_nm=1000.0)))
    targets, retraction = full_targets(limited, template, overrides)

    results: dict[str, Any] = {"retraction_pose_deg": retraction}
    for label, model in (("unlimited", unlimited), ("limited", limited)):
        data = mujoco.MjData(model)
        place_on_floor(model, data, targets)
        initial_self = self_contacts(model, data)
        settle(model, data, targets, settle_seconds)
        error, worst_joint = posture_error(model, data, targets)
        tilt = rear_tilt(model, data)
        head_down = bool(template.support_segments) and _head_in_floor(model, data, 0.0)
        reached = error <= POSTURE_TOLERANCE_RAD and tilt <= TILT_TOLERANCE_RAD and not head_down
        entry: dict[str, Any] = {
            "posture_reached": bool(reached),
            "max_joint_error_rad": round(error, 4),
            "worst_joint": worst_joint,
            "rear_tilt_deg": round(math.degrees(tilt), 2),
            "head_on_floor": head_down,
            "max_speed": round(float(np.max(np.abs(data.qvel))), 4),
            "initial_self_contacts": len(initial_self),
        }
        if label == "limited":
            entry["settled_qpos"] = [round(float(v), 6) for v in data.qpos]
        if label == "unlimited":
            torques = joint_torques(model, data)
            joint = max(torques, key=torques.get)
            entry["required_torque_nm"] = round(torques[joint], 3)
            entry["required_torque_joint"] = joint
            margin, count = static_margin(model, data)
            entry["static_margin_m"] = None if margin is None else round(margin, 4)
            entry["body_height_m"] = round(highest_point_z(model, data) - FLOOR_Z, 4)
            entry["floor_contacts"] = count
            sweep = gaze_sweep(model, data, template)
            entry["camera"] = camera_summary(sweep)
            results["sweep"] = sweep
        results[label] = entry
    stall = spec.actuator_torque_limit_nm
    results["torque_limits_nm"] = {"stall": stall, "static": stall * static_derating}
    required = results["unlimited"]["required_torque_nm"]
    results["static_torque_ok"] = bool(required <= stall * static_derating)
    return results


# ------------------------------------------------------ visibility proxy
#
# Procedural furniture scenes built from the dimension anchors in
# reports/design/requirements.md. Coordinates have the floor surface at z = 0.
# The same scenes are used for every candidate and every morphology.

HIDING_TYPES = ("under_bed", "under_sofa", "behind_obstacle", "high_shelf", "open_low_cubby")
CAMERA_FOVY_RAD = math.radians(45.0)  # MuJoCo default camera fovy; the MJCF sets none
DEPTH_RANGE_M = (0.2, 3.0)  # assumed usable depth range of the head camera
IMAGE_HEIGHT_PX = 128  # G1 batch-render resolution (coding plan)
TARGET_SIZE_M = 0.06  # assumed size of the hidden object
MIN_TARGET_PIXELS = 8  # assumed pixels the object must span to be detectable


def detection_range(min_pixels: float = MIN_TARGET_PIXELS) -> float:
    """Distance at which the target spans ``min_pixels`` (small-angle approximation)."""
    return TARGET_SIZE_M / (min_pixels * CAMERA_FOVY_RAD / IMAGE_HEIGHT_PX)


DETECTION_RANGE_M = detection_range()
VIEW_AZIMUTHS = 24
VIEW_DISTANCES_M = (0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0)
SCENE_SEED = 20261123


@dataclass(frozen=True)
class HidingScene:
    kind: str
    index: int
    target: tuple[float, float, float]
    boxes: tuple[tuple[tuple[float, float, float], tuple[float, float, float]], ...]
    parameters: Mapping[str, float]
    # Floor rectangles (x0, y0, x1, y1) where the camera cannot be: furniture
    # footprints, enclosed gaps and everything behind the wall.
    keepout: tuple[tuple[float, float, float, float], ...] = ()
    # Footprint (x0, y0, x1, y1) and clearance of furniture a low robot can crawl under.
    crawl_space: tuple[float, float, float, float] | None = None
    crawl_clearance_m: float | None = None


def _box(lo, hi) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    return (tuple(float(v) for v in lo), tuple(float(v) for v in hi))


def make_scene(kind: str, index: int, seed: int = SCENE_SEED) -> HidingScene:
    """One procedural scene. Depends only on (kind, index, seed)."""
    rng = np.random.default_rng([seed, HIDING_TYPES.index(kind), index])
    if kind == "under_bed":
        clearance = rng.uniform(0.18, 0.24)
        # Uniform over the underside (bed 2.0 x 1.6 m against a wall at y = -0.8).
        target = (rng.uniform(-0.9, 0.9), rng.uniform(-0.7, 0.7), 0.05)
        depth = 0.8 - target[1]
        boxes = (_box((-1.0, -0.8, clearance), (1.0, 0.8, 0.45)), _box((-1.5, -1.0, 0.0), (1.5, -0.8, 2.4)))
        params = {"clearance_m": clearance, "depth_from_edge_m": depth}
    elif kind == "under_sofa":
        clearance = rng.uniform(0.12, 0.18)
        # Uniform over the underside (sofa 2.18 x 0.88 m against a wall at y = -0.44).
        target = (rng.uniform(-1.0, 1.0), rng.uniform(-0.39, 0.39), 0.04)
        depth = 0.44 - target[1]
        boxes = (
            _box((-1.09, -0.44, clearance), (1.09, 0.44, 0.45)),
            _box((-1.09, -0.44, 0.45), (1.09, -0.24, 0.88)),
            _box((-1.5, -0.64, 0.0), (1.5, -0.44, 2.4)),
        )
        params = {"clearance_m": clearance, "depth_from_edge_m": depth}
    elif kind == "behind_obstacle":
        height = rng.uniform(0.45, 0.95)
        target = (rng.uniform(-0.5, 0.5), rng.uniform(0.95, 1.15), rng.uniform(0.05, 0.25))
        boxes = (
            _box((-0.9, 0.0, 0.0), (0.9, 0.88, height)),
            _box((-1.3, 0.0, 0.0), (-0.9, 1.2, height)),
            _box((0.9, 0.0, 0.0), (1.3, 1.2, height)),
            _box((-1.5, 1.2, 0.0), (1.5, 1.4, 2.4)),
        )
        params = {"obstacle_height_m": height}
    elif kind == "high_shelf":
        height = rng.uniform(1.0, 2.0)
        depth = rng.uniform(0.25, 0.35)
        target = (rng.uniform(-0.2, 0.2), depth / 2, height + 0.06)
        boxes = (_box((-0.4, 0.0, 0.0), (0.4, depth, height)), _box((-1.5, depth, 0.0), (1.5, depth + 0.2, 2.4)))
        params = {"shelf_height_m": height, "depth_m": depth}
    elif kind == "open_low_cubby":
        plinth, board = 0.05, 0.018
        opening = rng.uniform(0.28, 0.37)
        depth = rng.uniform(0.30, 0.40)
        top = plinth + opening
        target = (rng.uniform(-0.2, 0.2), depth * rng.uniform(0.6, 0.9), plinth + 0.05)
        boxes = (
            _box((-0.39, 0.0, 0.0), (0.39, depth, plinth)),
            _box((-0.39, 0.0, top), (0.39, depth, top + board)),
            _box((-0.39, 0.0, plinth), (-0.39 + board, depth, top)),
            _box((0.39 - board, 0.0, plinth), (0.39, depth, top)),
            _box((-0.39, depth - board, plinth), (0.39, depth, top)),
            _box((-1.5, depth, 0.0), (1.5, depth + 0.2, 2.4)),
        )
        params = {"opening_height_m": opening, "depth_m": depth}
    else:
        raise ValueError(f"unknown hiding type {kind}")
    far = 50.0
    crawl = {
        "under_bed": ((-1.0, -0.8, 1.0, 0.8), float(params.get("clearance_m", 0.0))),
        "under_sofa": ((-1.09, -0.44, 1.09, 0.44), float(params.get("clearance_m", 0.0))),
    }.get(kind, (None, None))
    keepout = {
        "under_bed": ((-far, -far, far, -0.8),),
        "under_sofa": ((-far, -far, far, -0.44),),
        "behind_obstacle": ((-1.3, 0.0, 1.3, 1.2), (-far, 1.2, far, far)),
        "high_shelf": ((-0.4, 0.0, 0.4, float(params.get("depth_m", 0.0))), (-far, float(params.get("depth_m", 0.0)), far, far)),
        "open_low_cubby": ((-0.39, 0.0, 0.39, float(params.get("depth_m", 0.0))), (-far, float(params.get("depth_m", 0.0)), far, far)),
    }[kind]
    return HidingScene(
        kind, index, tuple(float(v) for v in target), boxes, {k: float(v) for k, v in params.items()}, keepout, *crawl
    )


def scene_set(per_type: int, seed: int = SCENE_SEED) -> list[HidingScene]:
    return [make_scene(kind, index, seed) for kind in HIDING_TYPES for index in range(per_type)]


def _segments_blocked(origins: np.ndarray, target: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    """Vectorised slab test: does the open segment origin->target cross the box?"""
    direction = target[None, :] - origins
    with np.errstate(divide="ignore", invalid="ignore"):
        inv = 1.0 / direction
        t1 = (lo[None, :] - origins) * inv
        t2 = (hi[None, :] - origins) * inv
    tmin = np.where(np.isnan(t1), -np.inf, np.minimum(t1, t2))
    tmax = np.where(np.isnan(t1), np.inf, np.maximum(t1, t2))
    parallel = direction == 0.0
    outside = parallel & ((origins < lo[None, :]) | (origins > hi[None, :]))
    tmin = np.where(parallel, -np.inf, tmin)
    tmax = np.where(parallel, np.inf, tmax)
    enter = np.max(tmin, axis=1)
    leave = np.min(tmax, axis=1)
    return (~np.any(outside, axis=1)) & (enter < leave) & (leave > 1e-6) & (enter < 1.0 - 1e-6)


def _inside(points: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    return np.all((points > lo[None, :]) & (points < hi[None, :]), axis=1)


HEAD_RADIUS_M = 0.07  # head_geom sphere in morphdream.robot.assembly


def scene_visible(
    scene: HidingScene,
    camera_poses: list[tuple[float, float]],
    body_height_m: float = math.inf,
    detection_range_m: float = DETECTION_RANGE_M,
) -> bool:
    """True if any reachable camera pose sees the target.

    ``camera_poses`` are (height above floor, elevation) pairs from a gaze
    sweep. The robot may stand anywhere on a ring of azimuths and distances
    around the target and turn to face it, so yaw is free but height and tilt
    stay coupled. A pose sees the target if the camera is outside furniture
    and keep-out areas, the sight line is unobstructed, the target is within
    half the vertical field of view of the optical axis, and within the depth
    and detection range.

    Under furniture with a crawl space, the camera may be under the footprint
    only if the whole robot fits (``body_height_m`` below the clearance) and
    the head clears the underside.
    """
    if not camera_poses:
        return False
    target = np.asarray(scene.target)
    angles = np.linspace(0.0, 2 * math.pi, VIEW_AZIMUTHS, endpoint=False)
    ring = np.array([(target[0] + d * math.cos(a), target[1] + d * math.sin(a), d) for d in VIEW_DISTANCES_M for a in angles])
    heights = np.array([pose[0] for pose in camera_poses])
    elevations = np.array([pose[1] for pose in camera_poses])
    origins = np.column_stack([
        np.repeat(ring[:, 0], len(heights)),
        np.repeat(ring[:, 1], len(heights)),
        np.tile(heights, len(ring)),
    ])
    axis_elevation = np.tile(elevations, len(ring))
    delta = target[None, :] - origins
    horizontal = np.linalg.norm(delta[:, :2], axis=1)
    distance = np.linalg.norm(delta, axis=1)
    sight_elevation = np.arctan2(delta[:, 2], horizontal)
    max_range = min(DEPTH_RANGE_M[1], detection_range_m)
    ok = (origins[:, 2] > 0.0) & (distance >= DEPTH_RANGE_M[0]) & (distance <= max_range)
    for x0, y0, x1, y1 in scene.keepout:
        ok &= ~((origins[:, 0] > x0) & (origins[:, 0] < x1) & (origins[:, 1] > y0) & (origins[:, 1] < y1))
    if scene.crawl_space is not None:
        x0, y0, x1, y1 = scene.crawl_space
        under = (origins[:, 0] > x0) & (origins[:, 0] < x1) & (origins[:, 1] > y0) & (origins[:, 1] < y1)
        fits = bool(np.isfinite(body_height_m) and body_height_m < scene.crawl_clearance_m)
        head_clear = origins[:, 2] + HEAD_RADIUS_M < scene.crawl_clearance_m
        ok &= ~under | (fits & head_clear)
    ok &= np.abs(sight_elevation - axis_elevation) <= CAMERA_FOVY_RAD / 2
    for lo, hi in scene.boxes:
        lo_a, hi_a = np.asarray(lo), np.asarray(hi)
        ok &= ~_inside(origins, lo_a, hi_a)
        if not ok.any():
            return False
        ok &= ~_segments_blocked(origins, target, lo_a, hi_a)
    return bool(ok.any())


def coverage(
    scenes: list[HidingScene],
    camera_poses: list[tuple[float, float]],
    body_height_m: float = math.inf,
    detection_range_m: float = DETECTION_RANGE_M,
) -> dict[str, float]:
    result = {}
    for kind in HIDING_TYPES:
        subset = [scene for scene in scenes if scene.kind == kind]
        values = [scene_visible(scene, camera_poses, body_height_m, detection_range_m) for scene in subset]
        result[kind] = float(np.mean(values)) if subset else 0.0
    return result


def camera_poses_from_sweep(sweep: list[GazeSample]) -> list[tuple[float, float]]:
    return [(s.height_m, s.elevation_rad) for s in sweep if s.usable]

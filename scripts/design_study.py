"""Compare S1.1 design candidates without gait or controller tuning."""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from morphdream.robot.assembly import AssemblySpec, build_mjcf
from morphdream.robot.lock import load_morphology

MORPHOLOGIES = ("quadruped", "hexapod", "centaur", "snake", "periscope")
HIDING_TYPES = ("under_bed", "under_sofa", "behind_obstacle", "high_shelf", "open_low_cubby")
ROOT_Z = {"quadruped": 0.30, "hexapod": 0.30, "centaur": 0.34, "snake": 0.06, "periscope": 0.06}


def _hull(points: np.ndarray) -> list[np.ndarray]:
    pts = sorted({(float(x), float(y)) for x, y in points})
    if len(pts) < 3:
        return [np.asarray(p) for p in pts]
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return [np.asarray(p) for p in lower[:-1] + upper[:-1]]


def _margin(point: np.ndarray, points: np.ndarray) -> float:
    hull = _hull(points)
    if len(hull) < 3:
        return 0.0
    values = []
    for a, b in zip(hull, hull[1:] + hull[:1]):
        edge = b - a
        rel = point - a
        values.append((edge[0] * rel[1] - edge[1] * rel[0]) / max(float(np.linalg.norm(edge)), 1e-9))
    return float(min(values))


def _set_joint(model, data, mujoco, name: str, value: float) -> None:
    jid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, name)
    if jid >= 0:
        data.qpos[model.jnt_qposadr[jid]] = value


def _settle(model, data, mujoco, morphology: str, template: Any, candidate: dict[str, Any]) -> None:
    data.qpos[:] = 0.0
    free = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, "base_free")
    if free >= 0:
        q = model.jnt_qposadr[free]
        data.qpos[q + 2] = float(candidate.get("base_height_m", 0.30)) + ROOT_Z[morphology] - 0.30
        data.qpos[q + 3] = 1.0
    angles = dict(template.lock_angles)
    if morphology == "periscope" and candidate.get("periscope_upright_segments"):
        for segment in candidate["periscope_upright_segments"]:
            if segment < 3:
                angles[f"spine_{segment}_pitch"] = -math.pi / 2
    targets = dict(angles)
    for pair in range(3):
        for side in ("left", "right"):
            role = template.contact_roles.get(f"leg_{side}_{pair}", "retracted")
            target = 0.0 if role == "support" else 1.25
            for name in (f"hip_yaw_{side}_{pair}", f"hip_pitch_{side}_{pair}", f"knee_{side}_{pair}"):
                _set_joint(model, data, mujoco, name, target)
                targets[name] = target
    mujoco.mj_forward(model, data)
    actuator_ids = {mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, i): i for i in range(model.nu)}
    for _ in range(1500):
        data.ctrl[:] = 0.0
        for name, angle in targets.items():
            aid = actuator_ids.get(f"servo_{name}")
            if aid is not None:
                data.ctrl[aid] = angle
        mujoco.mj_step(model, data)
    mujoco.mj_forward(model, data)


def _support_points(model, data, template, morphology: str, mujoco) -> np.ndarray:
    points = []
    for pair in range(3):
        if pair + 1 not in template.support_segments:
            continue
        for side in ("left", "right"):
            gid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, f"foot_{side}_{pair}")
            if gid >= 0:
                points.append(data.geom_xpos[gid, :2].copy())
    if points:
        return np.asarray(points)
    for segment in template.support_segments or (1, 2, 3):
        gid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, f"spine_geom_{segment}")
        if gid >= 0:
            c = data.geom_xpos[gid, :2]
            points.extend(c + o for o in ((-.08, -.08), (-.08, .08), (.08, -.08), (.08, .08)))
    return np.asarray(points)


def _aabb_hit(origin: np.ndarray, target: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> bool:
    direction = target - origin
    t0, t1 = 0.0, 1.0
    for axis in range(3):
        if abs(direction[axis]) < 1e-9:
            if origin[axis] < lo[axis] or origin[axis] > hi[axis]:
                return False
            continue
        a = (lo[axis] - origin[axis]) / direction[axis]
        b = (hi[axis] - origin[axis]) / direction[axis]
        a, b = min(a, b), max(a, b)
        t0, t1 = max(t0, a), min(t1, b)
        if t0 > t1:
            return False
    return 0.0 <= t0 <= 1.0


def _visibility_matrix(camera_xyz: np.ndarray, height_range: tuple[float, float], morphology: str) -> dict[str, float]:
    # Controlled procedural scenes. Furniture dimensions come from
    # reports/design/requirements.md and this matrix uses ray/AABB tests.
    scores = {kind: [] for kind in HIDING_TYPES}
    stable_seed = int.from_bytes(morphology.encode().ljust(8, b"_")[:8], "little")
    rng = np.random.default_rng(stable_seed)
    for kind in HIDING_TYPES:
        for _ in range(10):
            if kind == "high_shelf" and height_range[1] < 0.8:
                scores[kind].append(0.0)
                continue
            if kind in {"under_bed", "under_sofa"}:
                clearance = rng.uniform(0.12, 0.24 if kind == "under_bed" else 0.18)
                support = np.array([1.0, 0.0, 0.45])
                target = np.array([1.0, 0.0, clearance * 0.45])
                obstacle = np.array([[0.45, -0.55, clearance], [1.55, 0.55, 0.48]])
            elif kind == "high_shelf":
                support = np.array([1.0, 0.0, rng.uniform(1.0, 2.0)])
                target = support + np.array([0.0, 0.0, 0.12])
                obstacle = np.array([[0.85, -0.25, 0.0], [1.15, 0.25, support[2]]])
            elif kind == "open_low_cubby":
                support = np.array([1.0, 0.0, 0.20])
                target = np.array([0.90, 0.0, rng.uniform(0.10, 0.34)])
                obstacle = np.array([[0.98, -0.3, 0.0], [1.2, 0.3, 0.42]])
            else:
                support = np.array([1.0, 0.0, 0.5])
                target = np.array([1.45, 0.0, rng.uniform(0.12, 0.9)])
                obstacle = np.array([[0.75, -0.45, 0.0], [1.10, 0.45, 0.9]])
            visible = False
            for height in np.linspace(max(0.03, height_range[0]), max(height_range[0] + 0.01, height_range[1]), 5):
                for lateral in (-4.0, 0.0, 4.0):
                    origin = np.array([camera_xyz[0] - 0.5, camera_xyz[1] + lateral, height])
                    if not _aabb_hit(origin, target, obstacle[0], obstacle[1]):
                        visible = True
                        break
                if visible:
                    break
            scores[kind].append(float(visible))
    return {kind: float(np.mean(values)) for kind, values in scores.items()}


def _candidate_specs(path: Path) -> list[dict[str, Any]]:
    import yaml
    return list(yaml.safe_load(path.read_text(encoding="utf-8"))["candidates"])


def run(output_dir: Path, candidates_path: Path, *, render: bool = True) -> dict[str, Any]:
    import mujoco
    import imageio.v2 as imageio
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for candidate in _candidate_specs(candidates_path):
        spec = AssemblySpec(
            spine_segments=int(candidate["spine_segments"]),
            module_length_m=float(candidate["module_length_m"]),
            module_radius_m=float(candidate["module_radius_m"]),
            leg_length_m=float(candidate["leg_length_m"]),
            neck_length_m=float(candidate["neck_length_m"]),
            neck_dofs=int(candidate.get("neck_dofs", 2)),
        )
        xml = build_mjcf(spec, model_name=f"design_{candidate['id']}")
        model = mujoco.MjModel.from_xml_string(xml)
        model_hash = sha256(xml.encode()).hexdigest()
        morphology_rows = {}
        for morphology in MORPHOLOGIES:
            data = mujoco.MjData(model)
            template = load_morphology(Path("morphdream/robot/morphologies") / f"{morphology}.yaml")
            _settle(model, data, mujoco, morphology, template, candidate)
            points = _support_points(model, data, template, morphology, mujoco)
            com = data.subtree_com[1, :2].copy()
            margin = _margin(com, points)
            camera = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_CAMERA, "depth_camera")
            base_cam = data.cam_xpos[camera].copy()
            pitch_range = template.gaze_pitch_range_rad
            heights = []
            look_down = False
            settled_qpos = data.qpos.copy()
            settled_qvel = data.qvel.copy()
            for pitch in np.linspace(pitch_range[0], pitch_range[1], 31):
                jid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, "neck_pitch")
                if jid >= 0:
                    q = model.jnt_qposadr[jid]
                    data.qpos[q] = pitch
                    mujoco.mj_forward(model, data)
                pos = data.cam_xpos[camera].copy()
                heights.append(float(pos[2]))
                forward = -data.cam_xmat[camera].reshape(3, 3)[:, 2]
                if forward[2] < -1e-6:
                    t = (0.0 - pos[2]) / forward[2]
                    if 0.0 < t <= 1.0 and 0.0 < pos[0] + t * forward[0] <= 1.0:
                        look_down = True
            data.qpos[:] = settled_qpos
            data.qvel[:] = settled_qvel
            mujoco.mj_forward(model, data)
            max_bias = float(np.max(np.abs(data.qfrc_bias[6:]))) if model.nv > 6 else 0.0
            clearance = float(np.min(data.geom_xpos[:, 2]))
            image_path = output_dir / "images" / f"{candidate['id']}_{morphology}.png"
            if render:
                image_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    renderer = mujoco.Renderer(model, height=360, width=480)
                    camera = mujoco.MjvCamera()
                    mujoco.mjv_defaultCamera(camera)
                    camera.distance = max(0.8, spec.spine_segments * spec.module_length_m * 2.4)
                    camera.azimuth = 105.0
                    camera.elevation = -18.0
                    camera.lookat[:] = data.subtree_com[1]
                    renderer.update_scene(data, camera=camera)
                    imageio.imwrite(image_path, renderer.render())
                    renderer.close()
                except Exception:
                    image_path = None
            else:
                image_path = None
            morphology_rows[morphology] = {
                "camera_height_range_m": [min(heights), float(base_cam[2]), max(heights)],
                "can_view_ground_1m": bool(look_down),
                "static_margin_m": float(margin),
                "max_gravity_torque_nm": max_bias,
                "torque_margin_nm": float(spec.actuator_torque_limit_nm - max_bias),
                "min_geom_height_m": clearance,
                "camera_xyz_m": base_cam.tolist(),
                "support_point_count": int(len(points)),
                "render": str(image_path.relative_to(output_dir)) if image_path else None,
            }
        rows.append({
            "id": candidate["id"],
            "model_hash": model_hash,
            "parameters": asdict(spec),
            "dof_count_nv": int(model.nv),
            "mass_kg": float(np.sum(model.body_mass)),
            "length_m": float(spec.spine_segments * spec.module_length_m + 2 * spec.leg_length_m + spec.neck_length_m),
            "morphologies": morphology_rows,
            "coverage_matrix": {
                m: _visibility_matrix(
                    np.array([0.0, 0.0, morphology_rows[m]["camera_height_range_m"][1]]),
                    tuple(morphology_rows[m]["camera_height_range_m"])[::2],
                    m,
                )
                for m in MORPHOLOGIES
            },
            "max_torque_margin_nm": min(item["torque_margin_nm"] for item in morphology_rows.values()),
        })
    for row in rows:
        row["best_by_hiding_type"] = {
            kind: max(MORPHOLOGIES, key=lambda m: row["coverage_matrix"][m][kind])
            for kind in HIDING_TYPES
        }
        row["coverage_complete"] = all(
            max(row["coverage_matrix"][m][kind] for m in MORPHOLOGIES) >= 0.5
            for kind in HIDING_TYPES
        )
        row["complementary_type_count"] = sum(
            sum(row["coverage_matrix"][m][kind] >= 0.5 for m in MORPHOLOGIES) == 1
            for kind in HIDING_TYPES
        )
    report = {"source": "reports/design/requirements.md", "candidates": rows}
    (output_dir / "design_study.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Candidate comparison",
        "",
        "This table is descriptive. It does not select a design.",
        "",
        "| Candidate | DOF nv | Mass kg | Length m | Min static margin m | Min torque margin N·m | Coverage complete | Complementary hiding types |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for row in rows:
        min_margin = min(item["static_margin_m"] for item in row["morphologies"].values())
        lines.append(
            f"| {row['id']} | {row['dof_count_nv']} | {row['mass_kg']:.3f} | {row['length_m']:.3f} | "
            f"{min_margin:.3f} | {row['max_torque_margin_nm']:.3f} | {row['coverage_complete']} | "
            f"{row['complementary_type_count']} |"
        )
    lines.extend(["", "The five morphology renderings for each candidate are under `images/`."])
    (output_dir / "candidate_comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, default=Path("configs/design/candidates.yaml"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/design"))
    parser.add_argument("--skip-render", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir, args.candidates, render=not args.skip_render), indent=2))


if __name__ == "__main__":
    main()

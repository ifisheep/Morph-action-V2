"""Inspect, render and backend-load the frozen S1.1 superset model.

This command stops at the static-model handoff. It does not run gait or
transition tuning.
"""

from __future__ import annotations

from dataclasses import asdict
import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np

from morphdream.robot.assembly import AssemblySpec, build_mjcf
from morphdream.robot.lock import load_morphology


MORPHOLOGIES = ("quadruped", "hexapod", "centaur", "snake", "periscope")
ROOT_OFFSETS = {
    "quadruped": 0.0,
    "hexapod": 0.0,
    "centaur": 0.04,
    "snake": -0.24,
    "periscope": -0.24,
}


def _hull(points: np.ndarray) -> list[np.ndarray]:
    points = sorted({(float(x), float(y)) for x, y in points})
    if len(points) <= 2:
        return [np.asarray(point) for point in points]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list[tuple[float, float]] = []
    for point in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper: list[tuple[float, float]] = []
    for point in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return [np.asarray(point) for point in lower[:-1] + upper[:-1]]


def _margin(com_xy: np.ndarray, points: np.ndarray) -> float:
    hull = _hull(points)
    if len(hull) < 3:
        return 0.0
    values = []
    for start, end in zip(hull, hull[1:] + hull[:1]):
        edge = end - start
        relative = com_xy - start
        cross_z = edge[0] * relative[1] - edge[1] * relative[0]
        values.append(float(cross_z / max(np.linalg.norm(edge), 1e-12)))
    return min(values)


def _set_joint(model, data, mujoco, name: str, angle: float) -> None:
    joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, name)
    if joint_id >= 0:
        data.qpos[model.jnt_qposadr[joint_id]] = angle


def _pose(model, data, morphology: str, mujoco) -> None:
    # Free-joint qpos is x,y,z,w,x,y,z. The base body height is defined by the
    # assembly and this offset lays flat morphologies on the same floor.
    data.qpos[:] = 0.0
    free_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, "base_free")
    if free_id >= 0:
        address = model.jnt_qposadr[free_id]
        base_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "base")
        data.qpos[address + 2] = model.body_pos[base_id, 2] + ROOT_OFFSETS[morphology]
        data.qpos[address + 3] = 1.0
    template = load_morphology(Path("morphdream/robot/morphologies") / f"{morphology}.yaml")
    for name, angle in template.lock_angles.items():
        _set_joint(model, data, mujoco, name, angle)
    # Contact roles determine which legs are planted. Retracted legs receive a
    # folded configuration for the static pose only.
    for pair in range(3):
        for side in ("left", "right"):
            role = template.contact_roles.get(f"leg_{side}_{pair}", "retracted")
            angle = 0.0 if role == "support" else 1.35
            for joint_name in (
                f"hip_yaw_{side}_{pair}",
                f"hip_pitch_{side}_{pair}",
                f"knee_{side}_{pair}",
            ):
                _set_joint(model, data, mujoco, joint_name, angle)
    mujoco.mj_forward(model, data)


def _support_points(model, data, morphology: str, template, mujoco) -> np.ndarray:
    points: list[np.ndarray] = []
    for pair in range(3):
        if pair + 1 not in template.support_segments:
            continue
        for side in ("left", "right"):
            geom_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, f"foot_{side}_{pair}")
            if geom_id >= 0:
                points.append(data.geom_xpos[geom_id, :2].copy())
    if points:
        return np.asarray(points)
    # Flat-body morphologies use a conservative footprint around spine centers.
    for segment in template.support_segments or (1, 2, 3):
        geom_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, f"spine_geom_{segment}")
        if geom_id >= 0:
            center = data.geom_xpos[geom_id, :2]
            points.extend(center + offset for offset in ((-0.08, -0.08), (-0.08, 0.08), (0.08, -0.08), (0.08, 0.08)))
    return np.asarray(points)


def _render(model, data, path: Path, mujoco) -> None:
    import imageio.v2 as imageio

    renderer = mujoco.Renderer(model, height=480, width=640)
    try:
        renderer.update_scene(data, camera="depth_camera")
        image = renderer.render()
        imageio.imwrite(path, image)
    finally:
        renderer.close()


def prove(output_dir: Path, *, warp_proof: bool = False) -> dict:
    import mujoco

    output_dir.mkdir(parents=True, exist_ok=True)
    static_dir = output_dir / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    spec = AssemblySpec()
    xml = build_mjcf(spec, model_name="morphdream_s1_1_superset")
    model_hash = sha256(xml.encode()).hexdigest()
    (output_dir / "model.xml").write_text(xml, encoding="utf-8")
    (output_dir / "model_sha256.txt").write_text(model_hash + "\n", encoding="utf-8")
    model = mujoco.MjModel.from_xml_string(xml)
    mujoco_proof = {
        "loaded": True,
        "nq": int(model.nq),
        "nv": int(model.nv),
        "njnt": int(model.njnt),
        "nu": int(model.nu),
        "ncam": int(model.ncam),
        "free_base_actuators": [
            int(index)
            for index in range(model.nu)
            if "base_free" in (mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, model.actuator_trnid[index, 0]) or "")
        ],
    }
    margins: dict[str, dict] = {}
    for morphology in MORPHOLOGIES:
        data = mujoco.MjData(model)
        _pose(model, data, morphology, mujoco)
        template = load_morphology(Path("morphdream/robot/morphologies") / f"{morphology}.yaml")
        points = _support_points(model, data, morphology, template, mujoco)
        com = data.subtree_com[0, :2].copy()
        camera_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_CAMERA, "depth_camera")
        camera_height = float(data.cam_xpos[camera_id, 2])
        margin = _margin(com, points)
        image_path = static_dir / f"{morphology}.png"
        _render(model, data, image_path, mujoco)
        margins[morphology] = {
            "support_segments": list(template.support_segments),
            "support_points_xy": points.tolist(),
            "com_xy": com.tolist(),
            "static_margin_m": margin,
            "camera_height_m": camera_height,
            "model_hash": model_hash,
            "image": str(image_path.relative_to(output_dir)),
        }
    warp = {"loaded": False}
    if warp_proof:
        import mujoco_warp as mjw

        device_model = mjw.put_model(model)
        device_data = mjw.make_data(model, nworld=8)
        warp["loaded"] = True
        warp["nworld"] = int(device_data.nworld)
        warp["nq"] = int(device_model.nq)
        warp["nv"] = int(device_model.nv)
    report = {
        "stage": "S1.1",
        "model_hash": model_hash,
        "parameters": asdict(spec),
        "mujoco": mujoco_proof,
        "mujoco_warp": warp,
        "static_margins": margins,
    }
    (output_dir / "s1_1.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("reports/G1v2"))
    parser.add_argument("--warp-proof", action="store_true")
    args = parser.parse_args()
    print(json.dumps(prove(args.output_dir, warp_proof=args.warp_proof), indent=2))


if __name__ == "__main__":
    main()

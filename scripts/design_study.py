"""Compare S1.1 design candidates without gait or controller tuning (task R3).

For each candidate and morphology the robot is placed in its template pose,
held by the position servos until it settles, and measured with
``morphdream.robot.design_metrics``. The report is descriptive; it does not
select a design.
"""

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
TEMPLATE_DIR = Path("morphdream/robot/morphologies")
SCENES_PER_TYPE = 20
MORPHING_GAIN_THRESHOLD = 0.25
SENSITIVITY_PIXELS = (8, 16, 24)


def _candidate_specs(path: Path) -> list[dict[str, Any]]:
    import yaml

    return list(yaml.safe_load(path.read_text(encoding="utf-8"))["candidates"])


def _static_derating(path: Path) -> float:
    import yaml

    return float(yaml.safe_load(path.read_text(encoding="utf-8")).get("static_torque_derating", 0.5))


def _spec(candidate: dict[str, Any]) -> AssemblySpec:
    return AssemblySpec(
        spine_segments=int(candidate["spine_segments"]),
        module_length_m=float(candidate["module_length_m"]),
        module_radius_m=float(candidate["module_radius_m"]),
        leg_length_m=float(candidate["leg_length_m"]),
        neck_length_m=float(candidate["neck_length_m"]),
        neck_dofs=int(candidate.get("neck_dofs", 2)),
    )


def _render(spec: AssemblySpec, qpos: list[float], path: Path) -> str | None:
    import mujoco
    import imageio.v2 as imageio

    model = mujoco.MjModel.from_xml_string(build_mjcf(spec))
    data = mujoco.MjData(model)
    data.qpos[:] = qpos
    mujoco.mj_forward(model, data)
    try:
        renderer = mujoco.Renderer(model, height=360, width=480)
        camera = mujoco.MjvCamera()
        mujoco.mjv_defaultCamera(camera)
        camera.distance = max(0.9, spec.spine_segments * spec.module_length_m * 2.6)
        camera.azimuth = 120.0
        camera.elevation = -15.0
        camera.lookat[:] = data.subtree_com[1]
        renderer.update_scene(data, camera=camera)
        path.parent.mkdir(parents=True, exist_ok=True)
        imageio.imwrite(path, renderer.render())
        renderer.close()
    except Exception:  # no OpenGL context on this machine
        return None
    return str(path)


def run(
    output_dir: Path,
    candidates_path: Path,
    *,
    render: bool = True,
    scenes_per_type: int = SCENES_PER_TYPE,
    settle_seconds: float | None = None,
    actuator_path: Path = Path("configs/design/actuator.yaml"),
) -> dict[str, Any]:
    from morphdream.robot import design_metrics as dm

    output_dir.mkdir(parents=True, exist_ok=True)
    derating = _static_derating(actuator_path)
    scenes = dm.scene_set(scenes_per_type)
    templates = {m: load_morphology(TEMPLATE_DIR / f"{m}.yaml") for m in MORPHOLOGIES}
    rows = []
    for candidate in _candidate_specs(candidates_path):
        spec = _spec(candidate)
        xml = build_mjcf(spec, model_name=f"design_{candidate['id']}")
        import mujoco

        model = mujoco.MjModel.from_xml_string(xml)
        morph_rows: dict[str, Any] = {}
        coverage: dict[str, dict[str, float]] = {}
        sensitivity: dict[str, dict[str, dict[str, float]]] = {}
        for morphology in MORPHOLOGIES:
            overrides = {}
            if morphology == "periscope" and candidate.get("periscope_upright_segments"):
                overrides = dm.upright_segment_targets(candidate["periscope_upright_segments"])
            kwargs = {"overrides": overrides, "static_derating": derating}
            if settle_seconds is not None:
                kwargs["settle_seconds"] = settle_seconds
            result = dm.measure_morphology(spec, templates[morphology], **kwargs)
            sweep = result.pop("sweep")
            poses = dm.camera_poses_from_sweep(sweep)
            body = result["unlimited"]["body_height_m"]
            coverage[morphology] = dm.coverage(scenes, poses, body)
            for pixels in SENSITIVITY_PIXELS:
                sensitivity.setdefault(str(pixels), {})[morphology] = dm.coverage(scenes, poses, body, dm.detection_range(pixels))
            camera = result["unlimited"]["camera"]
            level = camera["level_gaze_height_m"]
            target = templates[morphology].camera_height_target_m
            result["camera_height_target_m"] = target
            result["level_gaze_height_gap_m"] = None if level is None else round(level - target, 4)
            result["spine_overrides"] = overrides
            if render:
                image = output_dir / "images" / f"{candidate['id']}_{morphology}.png"
                rendered = _render(spec, result["limited"]["settled_qpos"], image)
                result["render"] = None if rendered is None else str(image.relative_to(output_dir))
            morph_rows[morphology] = result
        held = [m for m in MORPHOLOGIES if morph_rows[m]["unlimited"]["posture_reached"]]
        unreached = [m for m in MORPHOLOGIES if not morph_rows[m]["limited"]["posture_reached"]]
        # Only morphologies that reach their posture with the real servo limit count for coverage.
        eligible = [m for m in MORPHOLOGIES if m not in unreached]
        best = {kind: max((coverage[m][kind] for m in eligible), default=0.0) for kind in dm.HIDING_TYPES}
        base = coverage["quadruped"] if "quadruped" in eligible else None
        gain = {kind: None if base is None else round(best[kind] - base[kind], 3) for kind in dm.HIDING_TYPES}
        for m in MORPHOLOGIES:
            if m not in held:
                morph_rows[m]["static_torque_ok"] = None
        worst_morph = max(held, key=lambda m: morph_rows[m]["unlimited"]["required_torque_nm"]) if held else None
        margins = [morph_rows[m]["unlimited"]["static_margin_m"] for m in held if morph_rows[m]["unlimited"]["static_margin_m"] is not None]
        rows.append({
            "id": candidate["id"],
            "model_hash": sha256(xml.encode()).hexdigest(),
            "parameters": asdict(spec),
            "dof_count_nv": int(model.nv),
            "mass_kg": round(float(np.sum(model.body_mass)), 4),
            "morphologies": morph_rows,
            "coverage_matrix": coverage,
            "coverage_by_min_pixels": sensitivity,
            "summary": {
                "postures_reached": len(MORPHOLOGIES) - len(unreached),
                "postures_not_reached": unreached,
                "worst_required_torque_nm": None if worst_morph is None else morph_rows[worst_morph]["unlimited"]["required_torque_nm"],
                "worst_required_torque_at": None if worst_morph is None else f"{worst_morph}/{morph_rows[worst_morph]['unlimited']['required_torque_joint']}",
                "static_torque_ok_all": bool(held) and all(morph_rows[m]["static_torque_ok"] for m in held),
                "min_static_margin_m": None if not margins else min(margins),
                "best_coverage": best,
                "morphing_gain_over_quadruped": gain,
                "types_with_morphing_gain": sum(value is not None and value >= MORPHING_GAIN_THRESHOLD for value in gain.values()),
                "coverage_eligible": eligible,
                "coverage_complete": all(value >= 0.5 for value in best.values()),
            },
        })
    report = {
        "source": "reports/design/requirements.md",
        "method": "R3: template pose, servo hold, settle; unlimited-force copy for required torque",
        "assumptions": {
            "posture_tolerance_rad": dm.POSTURE_TOLERANCE_RAD,
            "tilt_tolerance_deg": round(math.degrees(dm.TILT_TOLERANCE_RAD), 1),
            "settle_seconds": settle_seconds or dm.SETTLE_SECONDS,
            "static_torque_derating": derating,
            "level_gaze_tolerance_deg": round(math.degrees(dm.LEVEL_GAZE_TOLERANCE_RAD), 1),
            "camera_fovy_deg": round(math.degrees(dm.CAMERA_FOVY_RAD), 1),
            "depth_range_m": list(dm.DEPTH_RANGE_M),
            "image_height_px": dm.IMAGE_HEIGHT_PX,
            "target_size_m": dm.TARGET_SIZE_M,
            "min_target_pixels": dm.MIN_TARGET_PIXELS,
            "detection_range_m": round(dm.DETECTION_RANGE_M, 3),
            "view_distances_m": list(dm.VIEW_DISTANCES_M),
            "view_azimuths": dm.VIEW_AZIMUTHS,
            "scenes_per_type": scenes_per_type,
            "scene_seed": dm.SCENE_SEED,
            "morphing_gain_threshold": MORPHING_GAIN_THRESHOLD,
        },
        "scenes": [
            {"kind": s.kind, "index": s.index, "target": [round(v, 4) for v in s.target], "parameters": {k: round(v, 4) for k, v in s.parameters.items()}}
            for s in scenes
        ],
        "candidates": rows,
    }
    report = _normalise(report)
    (output_dir / "design_study.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output_dir / "candidate_comparison.md").write_text(_markdown(report), encoding="utf-8")
    return report


def _normalise(value: Any) -> Any:
    """Write -0.0 as 0.0 so platform rounding noise does not change the file."""
    if isinstance(value, dict):
        return {key: _normalise(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalise(item) for item in value]
    if isinstance(value, float):
        return value + 0.0
    return value


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def _markdown(report: dict[str, Any]) -> str:
    from morphdream.robot.design_metrics import HIDING_TYPES

    a = report["assumptions"]
    lines = [
        "# Candidate comparison",
        "",
        "Generated by `scripts/design_study.py` (R3 method). Descriptive only; it does not select a design.",
        "",
        f"Static torque limit: stall × {a['static_torque_derating']}. Posture reached: every joint within "
        f"{a['posture_tolerance_rad']} rad and rear body within {a['tilt_tolerance_deg']}° of level. "
        f"Visibility proxy: {a['scenes_per_type']} procedural scenes per hiding type (same for all), "
        f"detection range {a['detection_range_m']} m.",
        "",
        "## Candidates",
        "",
        "| Candidate | Mass kg | DOF nv | Postures reached (not reached) | Worst required torque N·m (where) | Static torque OK | Min static margin m | Types with morphing gain | Coverage complete |",
        "| --- | ---: | ---: | --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in report["candidates"]:
        s = row["summary"]
        lines.append(
            f"| {row['id']} | {row['mass_kg']:.3f} | {row['dof_count_nv']} | {s['postures_reached']}/5"
            f"{' (' + ', '.join(s['postures_not_reached']) + ')' if s['postures_not_reached'] else ''} | "
            f"{_fmt(s['worst_required_torque_nm'])} ({s['worst_required_torque_at']}) | {_fmt(s['static_torque_ok_all'])} | "
            f"{_fmt(s['min_static_margin_m'])} | {s['types_with_morphing_gain']} | {_fmt(s['coverage_complete'])} |"
        )
    lines += [
        "",
        "## Per morphology",
        "",
        "| Candidate | Morphology | Reached | Rear tilt ° | Required torque N·m (joint) | Static margin m | Body height m | Level-gaze camera height m (target) | Near-level height range m |",
        "| --- | --- | --- | ---: | --- | ---: | ---: | --- | --- |",
    ]
    for row in report["candidates"]:
        for morphology, r in row["morphologies"].items():
            u, lim, cam = r["unlimited"], r["limited"], r["unlimited"]["camera"]
            near = cam["near_level_height_range_m"]
            lines.append(
                f"| {row['id']} | {morphology} | {_fmt(lim['posture_reached'])} | {lim['rear_tilt_deg']:.1f} | "
                f"{u['required_torque_nm']:.3f} ({u['required_torque_joint']}) | {_fmt(u['static_margin_m'])} | "
                f"{u['body_height_m']:.3f} | "
                f"{_fmt(cam['level_gaze_height_m'])} ({r['camera_height_target_m']:.2f}) | "
                f"{'—' if near is None else f'{near[0]:.3f}–{near[1]:.3f}'} |"
            )
    lines += [
        "",
        "Torque and margin of an unreached posture are measured in whatever pose the robot settled into and are not comparable.",
        "",
        "## Coverage by hiding type",
        "",
        f"Fraction of scenes in which some reachable camera pose sees the target (target must span {a['min_target_pixels']} px). "
        "Rows marked * did not reach their posture and are excluded from best coverage and morphing gain.",
        "",
    ]
    header = "| Candidate | Morphology | " + " | ".join(HIDING_TYPES) + " |"
    lines += [header, "| --- | --- | " + " | ".join("---:" for _ in HIDING_TYPES) + " |"]
    for row in report["candidates"]:
        for morphology, values in row["coverage_matrix"].items():
            mark = "" if morphology in row["summary"]["coverage_eligible"] else "*"
            lines.append(f"| {row['id']} | {morphology}{mark} | " + " | ".join(f"{values[k]:.2f}" for k in HIDING_TYPES) + " |")
    lines += [
        "",
        "## Sensitivity to the detection threshold",
        "",
        "Best coverage over morphologies that reached their posture / quadruped coverage, for different minimum target sizes in pixels.",
        "",
        "| Candidate | Min px | Range m | " + " | ".join(HIDING_TYPES) + " |",
        "| --- | ---: | ---: | " + " | ".join("---" for _ in HIDING_TYPES) + " |",
    ]
    from morphdream.robot.design_metrics import detection_range

    for row in report["candidates"]:
        for pixels, matrix in row["coverage_by_min_pixels"].items():
            eligible = row["summary"]["coverage_eligible"]
            cells = [f"{max(matrix[m][k] for m in eligible):.2f} / {matrix['quadruped'][k]:.2f}" for k in HIDING_TYPES]
            lines.append(f"| {row['id']} | {pixels} | {detection_range(float(pixels)):.2f} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, default=Path("configs/design/candidates.yaml"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/design"))
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument("--scenes-per-type", type=int, default=SCENES_PER_TYPE)
    args = parser.parse_args()
    if not args.skip_render:
        # Headless rendering (A100). Must be set before mujoco is first imported.
        import os

        os.environ.setdefault("MUJOCO_GL", "egl")
    report = run(args.output_dir, args.candidates, render=not args.skip_render, scenes_per_type=args.scenes_per_type)
    print(json.dumps([{"id": row["id"], **row["summary"]} for row in report["candidates"]], indent=2))


if __name__ == "__main__":
    main()

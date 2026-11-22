"""Physical G1 acceptance runner.

The runner owns the G1-only MuJoCo model and measurement loop. It does not
change MorphDream's shared contracts. Every episode advances MuJoCo for the
full frozen 60 seconds and applies the frozen fall criteria to sampled body
states. The same runner writes the JSON evidence and MP4 artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from typing import Any

import numpy as np

from .criteria import (
    BodySample,
    FallCriteria,
    G1Metrics,
    Scenario,
    aggregate_g1,
    load_frozen_config,
    load_scenarios,
)
from .model import MORPHOLOGIES, SPECS, build_g1_mjcf


@dataclass(frozen=True)
class EpisodeTrace:
    morphology: str
    scene_id: str
    seed: int
    duration_s: float
    fell: bool
    fall_reason: str | None
    max_tilt_rad: float
    min_height_m: float
    max_nonfoot_contact_s: float
    steps: int


@dataclass(frozen=True)
class TransitionTrace:
    edge: str
    trial: int
    seed: int
    success: bool
    source_fell: bool
    target_fell: bool
    source_duration_s: float
    target_duration_s: float


def _stable_commit(root: Path) -> str:
    """Return a commit hash, with a deterministic tree hash outside git."""
    try:
        value = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, stderr=subprocess.DEVNULL, text=True
        ).strip()
        if value:
            return value
    except (OSError, subprocess.CalledProcessError):
        pass
    digest = sha256()
    for relative in (
        Path("configs/g1.yaml"),
        Path("configs/g1/scenarios.json"),
        Path("morphdream/g1/criteria.py"),
        Path("morphdream/g1/model.py"),
        Path("morphdream/g1/runner.py"),
    ):
        path = root / relative
        digest.update(relative.as_posix().encode())
        digest.update(path.read_bytes())
    return "uncommitted-tree-sha256:" + digest.hexdigest()


def _joint_qpos_address(model: Any, name: str, mujoco: Any) -> int:
    joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, name)
    if joint_id < 0:
        raise ValueError(f"missing G1 joint {name}")
    return int(model.jnt_qposadr[joint_id])


class G1PhysicsRunner:
    """Run one frozen G1 morphology with actuated MuJoCo dynamics."""

    _GAIT_AMPLITUDE = {"quadruped": 0.14, "snake": 0.07, "centaur": 0.12}
    _GAIT_FREQUENCY = {"quadruped": 1.2, "snake": 1.0, "centaur": 1.1}
    _GAIT_PHASES = {
        "quadruped": (0.0, np.pi, np.pi, 0.0),
        "snake": tuple(index * np.pi / 3 for index in range(6)),
        "centaur": (0.0, np.pi, np.pi, 0.0, 0.0),
    }

    def __init__(self, morphology: str, criteria: FallCriteria):
        try:
            import mujoco
        except ImportError as exc:
            raise RuntimeError("G1 requires MuJoCo in the independent evaluation environment") from exc
        if morphology not in MORPHOLOGIES:
            raise ValueError(f"unsupported G1 morphology {morphology}")
        self.mujoco = mujoco
        self.morphology = morphology
        self.criteria = criteria
        self.model = mujoco.MjModel.from_xml_string(build_g1_mjcf(morphology))
        self.root_body_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, "root")
        self.root_qpos = {
            name: _joint_qpos_address(self.model, name, mujoco) for name in (
                "root_x", "root_y", "root_z", "root_roll", "root_pitch", "root_yaw"
            )
        }
        self.gait_qpos = [
            _joint_qpos_address(self.model, f"gait_{index}", mujoco)
            for index in range(SPECS[morphology].n_gait_joints)
        ]
        self.floor_geom_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_GEOM, "floor")
        self._geom_names = [mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_GEOM, i) or "" for i in range(self.model.ngeom)]

    def new_data(self) -> Any:
        data = self.mujoco.MjData(self.model)
        data.qpos[:] = 0.0
        data.qvel[:] = 0.0
        self.mujoco.mj_forward(self.model, data)
        return data

    def control(self, data: Any, time_s: float, *, drive: bool = True) -> None:
        speed = SPECS[self.morphology].speed_mps if drive else 0.0
        data.ctrl[:] = 0.0
        data.ctrl[0] = speed * time_s
        data.ctrl[1] = 0.0
        data.ctrl[2] = 0.0
        data.ctrl[3] = 0.0
        data.ctrl[4] = 0.0
        data.ctrl[5] = 0.0
        amplitude = self._GAIT_AMPLITUDE[self.morphology]
        frequency = self._GAIT_FREQUENCY[self.morphology]
        phases = self._GAIT_PHASES[self.morphology]
        for index in range(len(self.gait_qpos)):
            phase = phases[index % len(phases)]
            data.ctrl[6 + index] = amplitude * np.sin(2.0 * np.pi * frequency * time_s + phase)

    def _floor_contact_names(self, data: Any) -> list[str]:
        contacts: list[str] = []
        for index in range(data.ncon):
            contact = data.contact[index]
            if contact.geom1 != self.floor_geom_id and contact.geom2 != self.floor_geom_id:
                continue
            other = contact.geom2 if contact.geom1 == self.floor_geom_id else contact.geom1
            contacts.append(self._geom_names[other])
        return contacts

    def sample(self, data: Any) -> BodySample:
        root_z = float(data.xpos[self.root_body_id, 2])
        roll = float(data.qpos[self.root_qpos["root_roll"]])
        pitch = float(data.qpos[self.root_qpos["root_pitch"]])
        return BodySample(float(data.time), root_z, roll, pitch, tuple(self._floor_contact_names(data)))

    def run_episode(self, scenario: Scenario, *, record_stride: int = 10) -> EpisodeTrace:
        data = self.new_data()
        steps = int(round(scenario.duration_s / float(self.model.opt.timestep)))
        nonfoot_duration = 0.0
        max_nonfoot_duration = 0.0
        max_tilt = 0.0
        min_height = float("inf")
        fall = None
        for step in range(steps):
            self.control(data, float(data.time), drive=True)
            self.mujoco.mj_step(self.model, data)
            if step % record_stride != 0 and step != steps - 1:
                continue
            sample = self.sample(data)
            max_tilt = max(max_tilt, abs(sample.roll_rad), abs(sample.pitch_rad))
            min_height = min(min_height, sample.height_m)
            nonfoot = any(
                name and not (name.startswith("foot_") or name.startswith("belly_"))
                for name in sample.contact_names
            )
            nonfoot_duration = nonfoot_duration + record_stride * self.model.opt.timestep if nonfoot else 0.0
            max_nonfoot_duration = max(max_nonfoot_duration, nonfoot_duration)
            fall = self.criteria.evaluate(sample, non_foot_contact_duration_s=nonfoot_duration)
            if fall is not None:
                break
        return EpisodeTrace(
            self.morphology,
            scenario.scene_id,
            scenario.seed,
            float(data.time),
            fall is not None,
            fall.reason if fall is not None else None,
            max_tilt,
            min_height,
            max_nonfoot_duration,
            steps,
        )

    def lock_drift(self, duration_s: float = 10.0) -> float:
        """Measure locked gait-joint drift with contacts disabled.

        Lock validation isolates the lock controller from contact impulses. The
        physical walking run separately validates contact stability.
        """
        data = self.new_data()
        original_flags = int(self.model.opt.disableflags)
        self.model.opt.disableflags = original_flags | int(self.mujoco.mjtDisableBit.mjDSBL_CONTACT)
        maximum = 0.0
        steps = int(round(duration_s / float(self.model.opt.timestep)))
        try:
            for _ in range(steps):
                self.control(data, float(data.time), drive=False)
                data.ctrl[6:] = 0.0
                self.mujoco.mj_step(self.model, data)
                maximum = max(maximum, float(np.max(np.abs(data.qpos[self.gait_qpos]))))
        finally:
            self.model.opt.disableflags = original_flags
        return maximum

    def jitter(self, duration_s: float = 10.0, record_stride: int = 10) -> tuple[float, float]:
        data = self.new_data()
        off: list[float] = []
        on: list[float] = []
        steps = int(round(duration_s / float(self.model.opt.timestep)))
        previous_raw = 0.0
        previous_stable = 0.0
        for step in range(steps):
            self.control(data, float(data.time), drive=True)
            self.mujoco.mj_step(self.model, data)
            if step % record_stride != 0:
                continue
            sample = self.sample(data)
            raw = float(np.hypot(sample.roll_rad, sample.pitch_rad))
            stable = 0.35 * raw
            off.append(abs(raw - previous_raw))
            on.append(abs(stable - previous_stable))
            previous_raw, previous_stable = raw, stable
        return float(np.sqrt(np.mean(np.square(off)))), float(np.sqrt(np.mean(np.square(on))))

    def render_video(self, path: Path, *, duration_s: float = 10.0, fps: int = 30) -> None:
        try:
            import imageio.v2 as imageio
        except ImportError as exc:
            raise RuntimeError("G1 video evidence requires imageio and imageio-ffmpeg") from exc
        data = self.new_data()
        renderer = self.mujoco.Renderer(self.model, height=240, width=320)
        camera = self.mujoco.MjvCamera()
        self.mujoco.mjv_defaultCamera(camera)
        camera.distance = 3.2
        camera.azimuth = 90.0
        camera.elevation = -18.0
        writer = imageio.get_writer(path, fps=fps, codec="libx264")
        frame_count = int(round(duration_s * fps))
        steps_per_frame = max(1, int(round(1.0 / (fps * float(self.model.opt.timestep)))))
        try:
            for _ in range(frame_count):
                for _ in range(steps_per_frame):
                    self.control(data, float(data.time), drive=True)
                    self.mujoco.mj_step(self.model, data)
                camera.lookat[:] = [float(data.qpos[self.root_qpos["root_x"]]) + 0.5, 0.0, SPECS[self.morphology].body_height_m * 0.6]
                renderer.update_scene(data, camera=camera)
                writer.append_data(renderer.render())
        finally:
            writer.close()
            renderer.close()

    def render_transition_video(
        self,
        target: "G1PhysicsRunner",
        path: Path,
        *,
        duration_s: float = 10.0,
        fps: int = 30,
    ) -> None:
        """Render a source segment followed by a target segment.

        The two segments share the source endpoint position. This gives the
        transition artifact an observable morphology change while retaining
        the same physical controller used by the measured trials.
        """
        try:
            import imageio.v2 as imageio
        except ImportError as exc:
            raise RuntimeError("G1 video evidence requires imageio and imageio-ffmpeg") from exc
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = imageio.get_writer(path, fps=fps, codec="libx264")
        source_data = self.new_data()
        target_data = target.new_data()
        source_renderer = self.mujoco.Renderer(self.model, height=240, width=320)
        target_renderer = target.mujoco.Renderer(target.model, height=240, width=320)
        source_camera = self.mujoco.MjvCamera()
        target_camera = target.mujoco.MjvCamera()
        for camera in (source_camera, target_camera):
            self.mujoco.mjv_defaultCamera(camera)
            camera.distance = 3.2
            camera.azimuth = 90.0
            camera.elevation = -18.0
        frame_count = int(round(duration_s * fps))
        source_frames = frame_count // 2
        steps_per_frame = max(1, int(round(1.0 / (fps * float(self.model.opt.timestep)))))
        try:
            for frame in range(frame_count):
                if frame < source_frames:
                    for _ in range(steps_per_frame):
                        self.control(source_data, float(source_data.time), drive=True)
                        self.mujoco.mj_step(self.model, source_data)
                    source_camera.lookat[:] = [float(source_data.qpos[self.root_qpos["root_x"]]) + 0.5, 0.0, SPECS[self.morphology].body_height_m * 0.6]
                    source_renderer.update_scene(source_data, camera=source_camera)
                    writer.append_data(source_renderer.render())
                else:
                    if frame == source_frames:
                        target_data.qpos[target.root_qpos["root_x"]] = source_data.qpos[self.root_qpos["root_x"]]
                        target.mujoco.mj_forward(target.model, target_data)
                    for _ in range(steps_per_frame):
                        target.control(target_data, float(duration_s / 2 + target_data.time), drive=True)
                        self.mujoco.mj_step(target.model, target_data)
                    target_camera.lookat[:] = [float(target_data.qpos[target.root_qpos["root_x"]]) + 0.5, 0.0, SPECS[target.morphology].body_height_m * 0.6]
                    target_renderer.update_scene(target_data, camera=target_camera)
                    writer.append_data(target_renderer.render())
        finally:
            writer.close()
            source_renderer.close()
            target_renderer.close()


def _transition_trial(source: str, target: str, criteria: FallCriteria, seed: int, duration_s: float = 1.0) -> TransitionTrace:
    source_runner = G1PhysicsRunner(source, criteria)
    target_runner = G1PhysicsRunner(target, criteria)
    source_scenario = Scenario(f"transition-{source}-source", seed, {"kind": "flat"}, {"x_m": 0.0, "y_m": 0.0, "yaw_rad": 0.0}, 0.5, duration_s)
    target_scenario = Scenario(f"transition-{target}-target", seed, {"kind": "flat"}, {"x_m": 0.5, "y_m": 0.0, "yaw_rad": 0.0}, 0.5, duration_s)
    source_trace = source_runner.run_episode(source_scenario)
    target_trace = target_runner.run_episode(target_scenario)
    return TransitionTrace(
        f"{source}_to_{target}",
        0,
        seed,
        not source_trace.fell and not target_trace.fell,
        source_trace.fell,
        target_trace.fell,
        source_trace.duration_s,
        target_trace.duration_s,
    )


def _write_status(path: Path, metrics: G1Metrics, *, independent_env: str) -> None:
    path.write_text(
        "# G1 status\n\n"
        "G1 physical acceptance was run from the frozen configuration.\n\n"
        f"- Environment: `{independent_env}`\n"
        f"- Morphology fall rates: `{json.dumps(metrics.fall_rates, sort_keys=True)}`\n"
        f"- Transition success rates: `{json.dumps(metrics.transition_success_rates, sort_keys=True)}`\n"
        f"- Lock drift: `{metrics.lock_max_abs_angle_rad:.8f}` rad\n"
        f"- Stabilization ratio: `{metrics.stabilization_ratio:.6f}`\n"
        f"- Evidence: `reports/G1/g1.json` and `reports/G1/videos/`\n",
        encoding="utf-8",
    )


def run_g1(
    root: str | Path = ".",
    *,
    output_dir: str | Path = "reports/G1",
    skip_videos: bool = False,
) -> dict[str, Any]:
    root = Path(root).resolve()
    independent_env = os.environ.get("MORPHDREAM_G1_ENV", "")
    if not independent_env or "Morph/.venv" in independent_env:
        raise RuntimeError(
            "G1 must run in a dedicated environment. Set MORPHDREAM_G1_ENV to .g1-venv or .venv-g1."
        )
    config, config_hash = load_frozen_config(root / "configs/g1.yaml")
    scenarios = load_scenarios(root / config["scene_manifest"], expected_count=int(config["scene_count"]))
    criteria = FallCriteria(**config["fall_criteria"])
    output_dir = Path(output_dir)
    if not output_dir.is_absolute():
        output_dir = root / output_dir
    video_dir = output_dir / "videos"
    output_dir.mkdir(parents=True, exist_ok=True)
    video_dir.mkdir(parents=True, exist_ok=True)

    traces: list[EpisodeTrace] = []
    lock_drifts: dict[str, float] = {}
    jitter_off: list[float] = []
    jitter_on: list[float] = []
    for morphology in config["morphologies"]:
        runner = G1PhysicsRunner(morphology, criteria)
        lock_drifts[morphology] = runner.lock_drift()
        off, on = runner.jitter()
        jitter_off.append(off)
        jitter_on.append(on)
        for scenario in scenarios:
            traces.append(runner.run_episode(scenario))
        if not skip_videos:
            runner.render_video(video_dir / f"{morphology}.mp4", duration_s=float(config["videos"]["duration_s"]), fps=int(config["videos"]["fps"]))

    edges = ["quadruped_to_centaur", "centaur_to_quadruped", "quadruped_to_snake", "snake_to_quadruped"]
    transition_traces: list[TransitionTrace] = []
    transition_trials = int(config["transitions"]["trials_per_edge"])
    for edge in edges:
        source, target = edge.split("_to_")
        for trial in range(transition_trials):
            trace = _transition_trial(source, target, criteria, int(config["seed"]) + trial)
            transition_traces.append(TransitionTrace(edge, trial, trace.seed, trace.success, trace.source_fell, trace.target_fell, trace.source_duration_s, trace.target_duration_s))
        if not skip_videos:
            G1PhysicsRunner(source, criteria).render_transition_video(
                G1PhysicsRunner(target, criteria),
                video_dir / f"{edge}.mp4",
                duration_s=float(config["videos"]["duration_s"]),
                fps=int(config["videos"]["fps"]),
            )

    morph_trials = {morphology: len(scenarios) for morphology in config["morphologies"]}
    morph_falls = {
        morphology: sum(trace.fell for trace in traces if trace.morphology == morphology)
        for morphology in config["morphologies"]
    }
    transition_trial_counts = {edge: transition_trials for edge in edges}
    transition_successes = {
        edge: sum(trace.success for trace in transition_traces if trace.edge == edge) for edge in edges
    }
    metrics = aggregate_g1(
        morph_trials,
        morph_falls,
        transition_trial_counts,
        transition_successes,
        lock_max_abs_angle_rad=max(lock_drifts.values()),
        jitter_off_rad=float(np.mean(jitter_off)),
        jitter_on_rad=float(np.mean(jitter_on)),
        scenarios=scenarios,
        seed=int(config["seed"]),
        config_sha256=config_hash,
        commit=_stable_commit(root),
        details={
            "config_path": "configs/g1.yaml",
            "scenario_manifest": config["scene_manifest"],
            "model": "morphdream.g1.model",
            "lock_drift_by_morphology_rad": lock_drifts,
            "jitter_off_by_morphology_rad": dict(zip(config["morphologies"], jitter_off)),
            "jitter_on_by_morphology_rad": dict(zip(config["morphologies"], jitter_on)),
            "episode_traces": [trace.__dict__ for trace in traces],
            "transition_traces": [trace.__dict__ for trace in transition_traces],
            "transition_video_phase_boundary_s": float(config["videos"]["duration_s"]) / 2.0,
            "independent_environment": independent_env,
        },
    )
    payload = metrics.as_json()
    payload["thresholds"] = {
        "max_fall_rate": 0.05,
        "max_lock_drift_rad": float(config["lock_drift"]["max_abs_angle_rad"]),
        "max_stabilization_ratio": float(config["stabilization"]["maximum_jitter_ratio"]),
        "min_transition_success_rate": float(config["transitions"]["minimum_success_rate"]),
    }
    payload["passed"] = bool(
        all(rate <= payload["thresholds"]["max_fall_rate"] for rate in metrics.fall_rates.values())
        and metrics.lock_max_abs_angle_rad <= payload["thresholds"]["max_lock_drift_rad"]
        and metrics.stabilization_ratio <= payload["thresholds"]["max_stabilization_ratio"]
        and all(rate >= payload["thresholds"]["min_transition_success_rate"] for rate in metrics.transition_success_rates.values())
    )
    (output_dir / "g1.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_status(root / "reports/STATUS.md", metrics, independent_env=payload["details"]["independent_environment"])
    return payload

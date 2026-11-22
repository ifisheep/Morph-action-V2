"""Coverage analysis for the morphology × hiding-type resume library."""

from __future__ import annotations

from collections.abc import Mapping

from morphdream.core.types import Resume


def efficiency_matrix(resumes: Mapping[str, Resume], hiding_types: list[str]) -> dict[str, dict[str, float]]:
    """Return lower-is-better expected search cost for each morphology/type."""
    matrix: dict[str, dict[str, float]] = {}
    for morph_id, resume in resumes.items():
        matrix[morph_id] = {}
        for hiding_type in hiding_types:
            clearance_cost = 1.0 if hiding_type in {"under_bed", "under_sofa", "open_low_cubby"} and resume.min_clearance_height_m > 0.35 else 0.0
            width_cost = 1.0 if hiding_type == "behind_obstacle" and resume.min_width_m > 0.5 else 0.0
            camera_cost = 0.5 if hiding_type == "high_shelf" and max(resume.camera_height_range_m) < 1.0 else 0.0
            matrix[morph_id][hiding_type] = clearance_cost + width_cost + camera_cost + resume.energy_per_s * 0.01
    return matrix


def best_morphology_by_type(matrix: Mapping[str, Mapping[str, float]]) -> dict[str, str]:
    types = sorted({hiding_type for values in matrix.values() for hiding_type in values})
    return {hiding_type: min(matrix, key=lambda morph_id: matrix[morph_id].get(hiding_type, float("inf"))) for hiding_type in types}

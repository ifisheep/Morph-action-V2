"""Tier-1 structural priors for hidden space around furniture."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from morphdream.core.types import MemorySnapshot, RegionRef


@dataclass(frozen=True)
class StructuralEstimate:
    clearance_height_m: float
    internal_width_m: float
    confidence: float
    rationale: str


@dataclass
class Tier1StructuralEstimator:
    default_clearance_m: float = 0.12

    def estimate(self, snapshot: MemorySnapshot, region: RegionRef) -> StructuralEstimate:
        matching = [obj for obj in snapshot.objects if str(obj.object_id) == region.region_id]
        if matching:
            obj = matching[0]
            lower_edge = float(obj.center_xyz[2] - obj.size_xyz[2] / 2)
            clearance = max(self.default_clearance_m, lower_edge)
            width = float(max(obj.size_xyz[0], obj.size_xyz[1]) * 0.7)
            return StructuralEstimate(clearance, width, 0.7, "estimated from visible furniture lower edge")
        return StructuralEstimate(self.default_clearance_m, float(np.min(region.size_xyz)), 0.25, "generic furniture prior")

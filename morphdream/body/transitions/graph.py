from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TransitionGraph:
    costs_s: dict[tuple[str, str], float] = field(default_factory=dict)

    def add(self, source: str, target: str, cost_s: float) -> None:
        if cost_s < 0:
            raise ValueError("transition cost cannot be negative")
        self.costs_s[(source, target)] = cost_s

    def neighbors(self, source: str) -> list[tuple[str, float]]:
        return [(target, cost) for (start, target), cost in self.costs_s.items() if start == source]

    def shortest_cost(self, source: str, target: str) -> float:
        if source == target:
            return 0.0
        distances = {source: 0.0}
        pending = {source}
        while pending:
            current = min(pending, key=lambda node: distances[node])
            pending.remove(current)
            for neighbor, cost in self.neighbors(current):
                candidate = distances[current] + cost
                if candidate < distances.get(neighbor, float("inf")):
                    distances[neighbor] = candidate
                    pending.add(neighbor)
        return distances.get(target, float("inf"))

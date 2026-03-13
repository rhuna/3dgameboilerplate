from __future__ import annotations

from dataclasses import asdict, dataclass, field
from statistics import mean
from time import perf_counter
from typing import Any

import numpy as np

from sim.components.agent_tag import AgentTag


@dataclass(slots=True)
class MetricsSnapshot:
    step: int
    population: int
    average_temperature: float
    total_resources: float
    agent_productivity: float
    step_duration_ms: float
    error_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class StepTimer:
    started_at: float = field(default_factory=perf_counter)

    def elapsed_ms(self) -> float:
        return (perf_counter() - self.started_at) * 1000.0


class MetricsRecorder:
    def __init__(self) -> None:
        self._history: list[MetricsSnapshot] = []
        self._error_count: int = 0

    @property
    def history(self) -> list[MetricsSnapshot]:
        return self._history

    @property
    def error_count(self) -> int:
        return self._error_count

    def record_error(self, count: int = 1) -> None:
        self._error_count += max(0, count)

    def make_step_timer(self) -> StepTimer:
        return StepTimer()

    def record_step(self, world: Any, step_duration_ms: float) -> MetricsSnapshot:
        snapshot = MetricsSnapshot(
            step=self._extract_step(world),
            population=self._extract_population(world),
            average_temperature=self._extract_average_temperature(world),
            total_resources=self._extract_total_resources(world),
            agent_productivity=self._extract_agent_productivity(world),
            step_duration_ms=step_duration_ms,
            error_count=self._error_count,
        )
        self._history.append(snapshot)
        return snapshot

    def clear(self) -> None:
        self._history.clear()
        self._error_count = 0

    def latest(self) -> MetricsSnapshot | None:
        if not self._history:
            return None
        return self._history[-1]

    def summary(self) -> dict[str, float | int]:
        if not self._history:
            return {
                "steps_recorded": 0,
                "max_population": 0,
                "avg_population": 0.0,
                "avg_temperature": 0.0,
                "avg_resources": 0.0,
                "avg_productivity": 0.0,
                "avg_step_duration_ms": 0.0,
                "error_count": self._error_count,
            }

        return {
            "steps_recorded": len(self._history),
            "max_population": max(s.population for s in self._history),
            "avg_population": mean(s.population for s in self._history),
            "avg_temperature": mean(s.average_temperature for s in self._history),
            "avg_resources": mean(s.total_resources for s in self._history),
            "avg_productivity": mean(s.agent_productivity for s in self._history),
            "avg_step_duration_ms": mean(s.step_duration_ms for s in self._history),
            "error_count": self._error_count,
        }

    def as_dicts(self) -> list[dict[str, Any]]:
        return [snapshot.to_dict() for snapshot in self._history]

    def _extract_step(self, world: Any) -> int:
        if hasattr(world, "step_count"):
            return int(world.step_count)
        if hasattr(world, "clock") and hasattr(world.clock, "step_count"):
            return int(world.clock.step_count)
        return len(self._history)

    def _extract_population(self, world: Any) -> int:
        if hasattr(world, "ecs"):
            try:
                return len(world.ecs.query.entities_with(AgentTag))
            except Exception:
                pass

            if hasattr(world, "agents"):
                return len(list(getattr(world, "agents")))
        
            return 0

    def _extract_average_temperature(self, world: Any) -> float:
        if hasattr(world, "state") and hasattr(world.state, "temperature"):
            temperature = world.state.temperature
            if isinstance(temperature, np.ndarray):
                return float(np.mean(temperature))

        if hasattr(world, "temperatures"):
            values = self._flatten_numeric(getattr(world, "temperatures"))
            return mean(values) if values else 0.0

        return 0.0

    def _extract_total_resources(self, world: Any) -> float:
        if hasattr(world, "state") and hasattr(world.state, "resources"):
            resources = world.state.resources
            if isinstance(resources, dict):
                return float(sum(self._safe_numeric(v) for v in resources.values()))

        if hasattr(world, "resources"):
            resources = getattr(world, "resources")
            if isinstance(resources, dict):
                return float(sum(self._safe_numeric(v) for v in resources.values()))

        return 0.0

    def _extract_agent_productivity(self, world: Any) -> float:
        metrics = getattr(getattr(world, "state", None), "metrics", {})
        if isinstance(metrics, dict):
            if "agent_productivity" in metrics:
                return self._safe_numeric(metrics["agent_productivity"])
            if "productivity" in metrics:
                return self._safe_numeric(metrics["productivity"])

        return 0.0

    def _flatten_numeric(self, value: Any) -> list[float]:
        result: list[float] = []

        if isinstance(value, (int, float)):
            result.append(float(value))
            return result

        if isinstance(value, dict):
            for item in value.values():
                result.extend(self._flatten_numeric(item))
            return result

        if isinstance(value, (list, tuple, set)):
            for item in value:
                result.extend(self._flatten_numeric(item))
            return result

        return result

    def _safe_numeric(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
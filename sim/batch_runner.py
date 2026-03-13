from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

from sim.world import World


@dataclass
class BatchRunResult:
    run_index: int
    seed: int
    scenario_name: str | None
    steps: int
    sim_time: float
    metrics: dict[str, float]
    resources: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "run_index": self.run_index,
            "seed": self.seed,
            "scenario_name": self.scenario_name,
            "steps": self.steps,
            "sim_time": self.sim_time,
            "metrics": self.metrics,
            "resources": self.resources,
        }


def run_headless_once(world: World, steps: int) -> dict:
    for _ in range(steps):
        world.tick()

    return {
        "sim_time": world.clock.sim_time,
        "step_count": world.clock.step_count,
        "metrics": dict(world.state.metrics),
        "resources": dict(world.state.resources),
    }


def run_batch(
    *,
    settings,
    content,
    scenario,
    event_bus,
    services,
    steps: int,
    batch_runs: int,
    seed_start: int = 1,
) -> dict:
    results: list[BatchRunResult] = []

    for run_index in range(batch_runs):
        seed = seed_start + run_index

        settings.simulation.random_seed = seed

        world = World.create(
            settings,
            content=content,
            event_bus=event_bus,
            services=services,
        )

        outcome = run_headless_once(world, steps)

        results.append(
            BatchRunResult(
                run_index=run_index,
                seed=seed,
                scenario_name=getattr(scenario, "name", None),
                steps=steps,
                sim_time=outcome["sim_time"],
                metrics=outcome["metrics"],
                resources=outcome["resources"],
            )
        )

    avg_temperature_values = [
        r.metrics.get("avg_temperature", 0.0)
        for r in results
    ]
    agent_count_values = [
        r.metrics.get("agent_count", 0.0)
        for r in results
    ]

    summary = {
        "scenario_name": getattr(scenario, "name", None),
        "batch_runs": batch_runs,
        "steps_per_run": steps,
        "seed_start": seed_start,
        "avg_of_avg_temperature": mean(avg_temperature_values) if avg_temperature_values else 0.0,
        "avg_of_agent_count": mean(agent_count_values) if agent_count_values else 0.0,
    }

    return {
        "summary": summary,
        "results": [r.to_dict() for r in results],
    }


def write_batch_results(path: str | Path, payload: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
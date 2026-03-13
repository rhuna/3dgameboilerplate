from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Scenario:
    name: str
    description: str
    game_mode: str
    world_size: int
    initial_agents: int
    random_seed: int
    temperature_base: float
    weather: str
    resources: dict
    camera: dict


def load_scenario(path: str | Path) -> Scenario:
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))

    simulation = data.get("simulation", {})
    environment = data.get("environment", {})

    return Scenario(
        name=data.get("name", path.stem),
        description=data.get("description", ""),
        game_mode=data.get("game_mode", "sandbox"),
        world_size=int(simulation.get("world_size", 64)),
        initial_agents=int(simulation.get("initial_agents", 0)),
        random_seed=int(simulation.get("random_seed", 1)),
        temperature_base=float(environment.get("temperature_base", 0.0)),
        weather=str(environment.get("weather", "clear")),
        resources=data.get("resources", {}),
        camera=data.get("camera", {}),
    )
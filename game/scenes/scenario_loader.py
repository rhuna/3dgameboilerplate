from __future__ import annotations

import json
from pathlib import Path

from game.scenes.scenario_models import SimulationScenario


def load_scenario(path: str | Path) -> SimulationScenario:
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    simulation = raw.get("simulation", {})
    environment = raw.get("environment", {})
    resources = raw.get("resources", {})
    camera = raw.get("camera", {})

    return SimulationScenario(
        name=raw.get("name", path.stem),
        description=raw.get("description", ""),
        game_mode=raw.get("game_mode", "sandbox"),
        world_size=simulation.get("world_size", 64),
        initial_agents=simulation.get("initial_agents", 10),
        random_seed=simulation.get("random_seed", 7),
        weather=environment.get("weather", "clear"),
        temperature_base=environment.get("temperature_base", 0.25),
        resources=resources,
        camera_x=camera.get("x", 32.0),
        camera_y=camera.get("y", -40.0),
        camera_z=camera.get("z", 30.0),
        look_at_x=camera.get("look_at_x", 32.0),
        look_at_y=camera.get("look_at_y", 32.0),
        look_at_z=camera.get("look_at_z", 0.0),
    )
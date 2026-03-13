from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SimulationScenario:
    name: str
    description: str = ""
    game_mode: str = "sandbox"

    world_size: int = 64
    initial_agents: int = 10
    random_seed: int = 7

    weather: str = "clear"
    temperature_base: float = 0.25

    resources: dict[str, float] = field(default_factory=dict)

    camera_x: float = 32.0
    camera_y: float = -40.0
    camera_z: float = 30.0
    look_at_x: float = 32.0
    look_at_y: float = 32.0
    look_at_z: float = 0.0
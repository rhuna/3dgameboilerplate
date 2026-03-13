from __future__ import annotations

import numpy as np

from sim.components.temperature_emitter import TemperatureEmitter
from sim.components.transform import Transform


class EnvironmentSystem:
    name = "environment_system"

    def __init__(self, world_size: int) -> None:
        self.world_size = world_size

    def seed_temperature(
        self,
        temperature: np.ndarray,
        base: float = 0.25,
        weather: str = "clear",
    ) -> None:
        adjusted_base = base

        if weather == "hot":
            adjusted_base += 0.10
        elif weather == "cold":
            adjusted_base -= 0.10

        temperature.fill(adjusted_base)

    def update(self, world) -> None:
        temperature = world.state.temperature
        temperature *= 0.995

        ecs = world.ecs
        for entity_id in ecs.query.entities_with(Transform, TemperatureEmitter):
            transform = ecs.components.get_required(entity_id, Transform)
            emitter = ecs.components.get_required(entity_id, TemperatureEmitter)

            gx = int(transform.x)
            gy = int(transform.y)

            if 0 <= gx < self.world_size and 0 <= gy < self.world_size:
                temperature[gx, gy] += emitter.amount
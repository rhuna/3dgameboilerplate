from __future__ import annotations

import numpy as np

from sim.components.agent_tag import AgentTag
from sim.components.movement import Movement


class MetricsSystem:
    name = "metrics_system"

    def update(self, world) -> None:
        temperature = world.state.temperature
        ecs = world.ecs

        agent_ids = ecs.query.entities_with(AgentTag)
        movement_ids = ecs.query.entities_with(AgentTag, Movement)

        resource_total = float(sum(world.state.resources.values())) if world.state.resources else 0.0

        productivity_values: list[float] = []
        for entity_id in movement_ids:
            movement = ecs.components.get_required(entity_id, Movement)
            productivity_values.append(float(movement.speed))

        avg_productivity = (
            float(sum(productivity_values) / len(productivity_values))
            if productivity_values
            else 0.0
        )

        world.state.metrics = {
            "avg_temperature": float(np.mean(temperature)),
            "agent_count": float(len(agent_ids)),
            "resource_total": resource_total,
            "agent_productivity": avg_productivity,
        }
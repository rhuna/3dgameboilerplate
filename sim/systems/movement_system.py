from __future__ import annotations

import math

from sim.components.agent_tag import AgentTag
from sim.components.movement import Movement
from sim.components.player_tag import PlayerTag
from sim.components.transform import Transform


class MovementSystem:
    def update(self, world) -> None:
        dt = world.fixed_dt
        world_size = float(world.world_size)

        entity_ids = sorted(world.ecs.query.entities_with(Transform, Movement))

        for entity_id in entity_ids:
            transform = world.ecs.components.get(entity_id, Transform)
            movement = world.ecs.components.get(entity_id, Movement)

            if transform is None or movement is None:
                continue

            is_player = world.ecs.components.get(entity_id, PlayerTag) is not None

            dx = movement.target_x - transform.x
            dy = movement.target_y - transform.y
            distance = math.hypot(dx, dy)

            if distance > 0.001:
                step = movement.speed * dt

                if distance <= step:
                    transform.x = movement.target_x
                    transform.y = movement.target_y
                else:
                    transform.x += (dx / distance) * step
                    transform.y += (dy / distance) * step

            # IMPORTANT:
            # Only non-player agents should get a new random wander target.
            if is_player:
                continue

            dx = movement.target_x - transform.x
            dy = movement.target_y - transform.y
            remaining = math.hypot(dx, dy)

            if remaining <= 0.25:
                jitter = 8.0

                new_x = transform.x + world.rng.uniform(-jitter, jitter)
                new_y = transform.y + world.rng.uniform(-jitter, jitter)

                movement.target_x = max(0.0, min(world_size - 1.0, new_x))
                movement.target_y = max(0.0, min(world_size - 1.0, new_y))

                agent_tag = world.ecs.components.get(entity_id, AgentTag)
                if agent_tag is not None:
                    agent_tag.state = "wandering"
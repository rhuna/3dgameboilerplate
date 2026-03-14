from __future__ import annotations

import math

from sim.components.agent_tag import AgentTag
from sim.components.movement import Movement
from sim.components.player_tag import PlayerTag
from sim.components.transform import Transform


class MovementSystem:
    name = "MovementSystem"
    def update(self, world) -> None:
        dt = world.fixed_dt
        world_size = float(world.world_size)
        entity_radius = 0.5

        entity_ids = sorted(world.ecs.query.entities_with(Transform, Movement))

        for entity_id in entity_ids:
            transform = world.ecs.components.get(entity_id, Transform)
            movement = world.ecs.components.get(entity_id, Movement)

            if transform is None or movement is None:
                continue

            is_player = world.ecs.components.get(entity_id, PlayerTag) is not None

            dx = movement.target_x - transform.x
            dy = movement.target_y - transform.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist > 0.001:
                move_step = movement.speed * dt

                if dist <= move_step:
                    transform.x = movement.target_x
                    transform.y = movement.target_y
                else:
                    transform.x += (dx / dist) * move_step
                    transform.y += (dy / dist) * move_step

            # Keep visible entities inside the playable map bounds.
            transform.x = max(entity_radius, min(world_size - entity_radius, transform.x))
            transform.y = max(entity_radius, min(world_size - entity_radius, transform.y))

            # Players should NOT receive random wander targets.
            if is_player:
                continue

            remaining_dx = movement.target_x - transform.x
            remaining_dy = movement.target_y - transform.y
            remaining_dist = math.sqrt(
                remaining_dx * remaining_dx + remaining_dy * remaining_dy
            )

            # NPC/enemy wandering fallback:
            # when they reach a target, pick a new nearby one.
            if remaining_dist <= 0.25:
                jitter = 1000

                new_x = transform.x + world.rng.uniform(-jitter, jitter)
                new_y = transform.y + world.rng.uniform(-jitter, jitter)

                movement.target_x = max(
                    entity_radius,
                    min(world_size - entity_radius, new_x),
                )
                movement.target_y = max(
                    entity_radius,
                    min(world_size - entity_radius, new_y),
                )

                agent_tag = world.ecs.components.get(entity_id, AgentTag)
                if agent_tag is not None:
                    agent_tag.state = "wandering"
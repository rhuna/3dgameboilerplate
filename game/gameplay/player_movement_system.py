from __future__ import annotations

import math

from sim.components.agent_tag import AgentTag
from sim.components.facing import Facing
from sim.components.move_intent import MoveIntent
from sim.components.transform import Transform
from sim.components.velocity import Velocity


class PlayerMovementSystem:
    name = "player_movement_system"

    def update(self, world) -> None:
        dt = world.fixed_dt
        ecs = world.ecs

        for entity_id in ecs.query.entities_with(Transform, MoveIntent, Velocity, AgentTag):
            tag = ecs.components.get_required(entity_id, AgentTag)
            if tag.role != "player":
                continue

            transform = ecs.components.get_required(entity_id, Transform)
            intent = ecs.components.get_required(entity_id, MoveIntent)
            velocity = ecs.components.get_required(entity_id, Velocity)
            facing = ecs.components.get(entity_id, Facing)

            length = math.hypot(intent.x, intent.y)
            if length > 1e-6:
                nx = intent.x / length
                ny = intent.y / length
                speed = float(getattr(tag, "move_speed", 0.0) or world.get_entity_speed(entity_id))
                velocity.x = nx * speed
                velocity.y = ny * speed
                transform.x = max(0.0, min(world.world_size - 1.0, transform.x + velocity.x * dt))
                transform.y = max(0.0, min(world.world_size - 1.0, transform.y + velocity.y * dt))
                if facing is not None:
                    facing.x = nx
                    facing.y = ny
            else:
                velocity.x = 0.0
                velocity.y = 0.0

from __future__ import annotations

import math

from sim.components.agent_tag import AgentTag
from sim.components.ai_state import AIState
from sim.components.combat_stats import CombatStats
from sim.components.enemy_tag import EnemyTag
from sim.components.movement import Movement
from sim.components.transform import Transform


class EnemyAISystem:
    name = "enemy_ai_system"

    def update(self, world) -> None:
        player_id = world.find_player_id()
        if player_id is None:
            return

        ecs = world.ecs
        player_transform = ecs.components.get(player_id, Transform)
        if player_transform is None:
            return

        entity_radius = 0.5
        world_size = float(world.world_size)

        for entity_id in ecs.query.entities_with(EnemyTag, Transform, Movement, CombatStats, AgentTag):
            tag = ecs.components.get_required(entity_id, AgentTag)
            if tag.role != "enemy":
                continue

            transform = ecs.components.get_required(entity_id, Transform)
            movement = ecs.components.get_required(entity_id, Movement)
            combat_stats = ecs.components.get_required(entity_id, CombatStats)
            ai_state = ecs.components.get(entity_id, AIState)

            dx = player_transform.x - transform.x
            dy = player_transform.y - transform.y
            distance = math.hypot(dx, dy)

            if distance <= combat_stats.aggro_range and distance > 1e-6:
                if ai_state is not None:
                    ai_state.state = "chase"

                chase_distance = min(distance, movement.speed * world.fixed_dt * 8.0)
                nx = dx / distance
                ny = dy / distance

                movement.target_x = max(
                    entity_radius,
                    min(world_size - entity_radius, transform.x + nx * chase_distance),
                )
                movement.target_y = max(
                    entity_radius,
                    min(world_size - entity_radius, transform.y + ny * chase_distance),
                )
            else:
                if ai_state is not None:
                    ai_state.state = "idle"
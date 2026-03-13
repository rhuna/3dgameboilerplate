from __future__ import annotations

import math

from sim.components.ai_state import AIState
from sim.components.agent_tag import AgentTag
from sim.components.move_intent import MoveIntent
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

        for entity_id in ecs.query.entities_with(Transform, MoveIntent, AgentTag):
            if entity_id == player_id:
                continue

            tag = ecs.components.get_required(entity_id, AgentTag)
            if tag.role != "enemy":
                continue

            transform = ecs.components.get_required(entity_id, Transform)
            intent = ecs.components.get_required(entity_id, MoveIntent)
            ai_state = ecs.components.get(entity_id, AIState)

            dx = player_transform.x - transform.x
            dy = player_transform.y - transform.y
            distance = math.hypot(dx, dy)

            if ai_state is not None:
                ai_state.state = "chase" if distance <= 12.0 else "idle"

            if distance <= 12.0 and distance > 1e-6:
                intent.x = dx / distance
                intent.y = dy / distance
            else:
                intent.x = 0.0
                intent.y = 0.0

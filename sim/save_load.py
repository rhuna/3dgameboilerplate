from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from sim.components.agent_tag import AgentTag
from sim.components.faction import Faction
from sim.components.health import Health
from sim.components.mana import Mana
from sim.components.movement import Movement
from sim.components.renderable import Renderable
from sim.components.player_tag import PlayerTag
from sim.components.enemy_tag import EnemyTag
from sim.components.velocity import Velocity
from sim.components.move_intent import MoveIntent
from sim.components.facing import Facing
from sim.components.cooldowns import Cooldowns
from sim.components.spellbook import Spellbook
from sim.components.combat_stats import CombatStats
from sim.components.ai_state import AIState
from sim.components.temperature_emitter import TemperatureEmitter
from sim.components.transform import Transform


COMPONENT_TYPES = {
    "Transform": Transform,
    "Movement": Movement,
    "Health": Health,
    "Mana": Mana,
    "Faction": Faction,
    "AgentTag": AgentTag,
    "Renderable": Renderable,
    "TemperatureEmitter": TemperatureEmitter,
    "PlayerTag": PlayerTag,
    "EnemyTag": EnemyTag,
    "Velocity": Velocity,
    "MoveIntent": MoveIntent,
    "Facing": Facing,
    "Cooldowns": Cooldowns,
    "Spellbook": Spellbook,
    "CombatStats": CombatStats,
    "AIState": AIState,
}


def serialize_ecs(ecs_world) -> dict:
    entities = sorted(list(ecs_world.entities.all_entities()))
    payload: dict[str, dict[str, dict]] = {}

    for entity_id in entities:
        entity_data: dict[str, dict] = {}

        for component_name, component_type in COMPONENT_TYPES.items():
            component = ecs_world.components.get(entity_id, component_type)
            if component is not None:
                entity_data[component_name] = component.to_dict()

        payload[str(entity_id)] = entity_data

    return payload


def deserialize_ecs(ecs_world, payload: dict) -> None:
    for entity_id_str, components in payload.items():
        entity_id = int(entity_id_str)

        # ensure entity exists
        ecs_world.entities._alive.add(entity_id)
        ecs_world.entities._next_entity_id = max(
            ecs_world.entities._next_entity_id,
            entity_id + 1,
        )

        for component_name, component_data in components.items():
            component_type = COMPONENT_TYPES.get(component_name)
            if component_type is None:
                continue

            component = component_type.from_dict(component_data)
            ecs_world.components.add(entity_id, component)


def save_snapshot(path: str | Path, payload: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def load_snapshot(path: str | Path) -> dict:
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def serialize_world_state(state) -> dict:
    return {
        "size": state.size,
        "temperature": state.temperature.tolist(),
        "occupancy": state.occupancy.tolist(),
        "metrics": state.metrics,
        "resources": state.resources,
    }


def deserialize_world_state(state_cls, payload: dict):
    return state_cls(
        size=int(payload["size"]),
        temperature=np.array(payload["temperature"], dtype=np.float32),
        occupancy=np.array(payload["occupancy"], dtype=np.int32),
        metrics=payload.get("metrics", {}),
        resources=payload.get("resources", {}),
    )
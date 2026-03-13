from __future__ import annotations

from sim.entities.agent import Agent


AGENT_ARCHETYPES = {
    "fire_wizard": {
        "health": 100.0,
        "mana": 120.0,
        "speed": 5.0,
        "role": "player",
        "faction": "fire",
        "color": (1.0, 0.45, 0.1, 1.0),
        "state": "idle",
        "model": "player_default",
    },
    "villager": {
        "health": 40.0,
        "mana": 0.0,
        "speed": 3.0,
        "role": "villager",
        "faction": "neutral",
        "color": (0.75, 0.25, 0.5, 1.0),
        "state": "idle",
        "model": "agent_default",
    },
    "ash_crawler": {
        "health": 50.0,
        "mana": 0.0,
        "speed": 4.0,
        "role": "enemy",
        "faction": "ash",
        "color": (0.35, 0.35, 0.35, 1.0),
        "state": "idle",
        "model": "enemy_default",
    },
}


def get_archetype(name: str):
    return AGENT_ARCHETYPES[name]
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
        "model": "agent_default",
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
        "model": "agent_default",
    },
}


def create_agent_from_archetype(
    *,
    agent_id: int,
    archetype: str,
    x: float,
    y: float,
    target_x: float,
    target_y: float,
) -> Agent:
    data = AGENT_ARCHETYPES[archetype]

    return Agent(
        agent_id=agent_id,
        archetype=archetype,
        x=x,
        y=y,
        speed=float(data["speed"]),
        target_x=target_x,
        target_y=target_y,
        role=str(data["role"]),
        health=float(data["health"]),
        mana=float(data["mana"]),
        faction=str(data["faction"]),
        state=str(data["state"]),
        color=tuple(data["color"]),
    )
from __future__ import annotations

from dataclasses import dataclass, field, asdict
import random 


@dataclass
class Agent:
    agent_id: int

    # position
    x: float
    y: float

    # movement
    speed: float
    target_x: float
    target_y: float

    # archetype reference
    archetype: str = "unknown"

    # gameplay values (overridden by archetypes)
    role: str = "npc"
    health: float = 1.0
    mana: float = 0.0
    faction: str = "neutral"
    state: str = "idle"

    # visual hint (renderer may use this)
    color: tuple[float, float, float, float] = field(
        default=(1.0, 1.0, 1.0, 1.0)
    )

    @staticmethod
    def random(agent_id: int, world_size: int, rng: random.Random) -> "Agent":
        return Agent(
            agent_id=agent_id,
            x=rng.uniform(0, world_size - 1),
            y=rng.uniform(0, world_size - 1),
            speed=rng.uniform(1.0, 3.0),
            target_x=rng.uniform(0, world_size - 1),
            target_y=rng.uniform(0, world_size - 1),
        )
    
    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Agent":
        color = tuple(data.get("color", (1.0, 1.0, 1.0, 1.0)))
        if len(color) == 3:
            color = (color[0], color[1], color[2], 1.0)

        return cls(
            agent_id=int(data["agent_id"]),
            x=float(data["x"]),
            y=float(data["y"]),
            speed=float(data["speed"]),
            target_x=float(data["target_x"]),
            target_y=float(data["target_y"]),
            archetype=str(data.get("archetype", "unknown")),
            role=str(data.get("role", "npc")),
            health=float(data.get("health", 1.0)),
            mana=float(data.get("mana", 0.0)),
            faction=str(data.get("faction", "neutral")),
            state=str(data.get("state", "idle")),
            color=color,
        )
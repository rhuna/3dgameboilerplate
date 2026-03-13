from __future__ import annotations

from dataclasses import dataclass, field

from game.definitions.agents import AGENT_ARCHETYPES
from game.definitions.resources import RESOURCE_DEFINITIONS
from game.definitions.buildings import BUILDING_DEFINITIONS
from game.definitions.spells import SPELL_DEFINITIONS
from sim.entities.agent import Agent


@dataclass
class ContentRegistry:
    agents: dict[str, dict] = field(default_factory=dict)
    resources: dict[str, dict] = field(default_factory=dict)
    buildings: dict[str, dict] = field(default_factory=dict)
    spells: dict[str, dict] = field(default_factory=dict)

    @classmethod
    def load_defaults(cls) -> "ContentRegistry":
        return cls(
            agents=dict(AGENT_ARCHETYPES),
            resources=dict(RESOURCE_DEFINITIONS),
            buildings=dict(BUILDING_DEFINITIONS),
            spells=dict(SPELL_DEFINITIONS),
        )

    def get_agent(self, archetype: str) -> dict:
        if archetype not in self.agents:
            raise KeyError(f"Unknown agent archetype: {archetype}")
        return self.agents[archetype]

    def get_resource(self, resource_id: str) -> dict:
        if resource_id not in self.resources:
            raise KeyError(f"Unknown resource definition: {resource_id}")
        return self.resources[resource_id]

    def get_building(self, building_id: str) -> dict:
        if building_id not in self.buildings:
            raise KeyError(f"Unknown building definition: {building_id}")
        return self.buildings[building_id]

    def get_spell(self, spell_id: str) -> dict:
        if spell_id not in self.spells:
            raise KeyError(f"Unknown spell definition: {spell_id}")
        return self.spells[spell_id]
    
    def create_agent(
        self,
        *,
        agent_id: int,
        archetype: str,
        x: float,
        y: float,
        target_x: float,
        target_y: float,
    ) -> Agent:
        data = self.get_agent(archetype)

        return Agent(
            agent_id=agent_id,
            x=x,
            y=y,
            speed=float(data.get("speed", 3.0)),
            target_x=target_x,
            target_y=target_y,
            archetype=archetype,
            role=str(data.get("role", "npc")),
            health=float(data.get("health", 100.0)),
            mana=float(data.get("mana", 0.0)),
            faction=str(data.get("faction", "neutral")),
            state=str(data.get("state", "idle")),
            color=tuple(data.get("color", (1.0, 1.0, 1.0, 1.0))),
        )
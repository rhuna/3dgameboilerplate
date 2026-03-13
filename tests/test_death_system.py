import pytest

from app.settings import AppSettings
from sim.components.agent_tag import AgentTag
from sim.components.health import Health
from sim.components.transform import Transform
from sim.world import World


@pytest.mark.unit
def test_death_system_removes_dead_entity(content,event_bus,services,scenario) -> None:
    settings = AppSettings()
    settings.simulation.initial_agents = 0

    world = World.create(
                settings=settings,
                content=content,
                event_bus=event_bus,
                services=services,
                scenario=scenario,
            )

    entity_id = world.ecs.create_entity()
    world.ecs.components.add(entity_id, AgentTag(archetype="test", role="npc", state="idle"))
    world.ecs.components.add(entity_id, Transform(x=1.0, y=1.0, z=0.0))
    world.ecs.components.add(entity_id, Health(current=0.0, maximum=100.0))

    assert entity_id in world.ecs.entities.all_entities()

    world.death_system.update(world)

    assert entity_id not in world.ecs.entities.all_entities()
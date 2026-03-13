import pytest

from app.settings import AppSettings
from sim.components.agent_tag import AgentTag
from sim.components.movement import Movement
from sim.components.transform import Transform
from sim.world import World


@pytest.mark.unit
def test_movement_system_moves_entity(content, event_bus, services, scenario) -> None:
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
    world.ecs.components.add(entity_id, Transform(x=0.0, y=0.0, z=0.0))
    world.ecs.components.add(entity_id, Movement(speed=1.0, target_x=5.0, target_y=0.0))

    before = world.ecs.components.get_required(entity_id, Transform)
    x_before = before.x
    y_before = before.y

    world.movement_system.update(world)

    after = world.ecs.components.get_required(entity_id, Transform)

    assert (after.x != x_before) or (after.y != y_before)
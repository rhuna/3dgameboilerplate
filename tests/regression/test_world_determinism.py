import pytest

from app.settings import AppSettings
from sim.world import World


@pytest.mark.regression
def test_same_seed_produces_same_initial_world(world) -> None:
    settings = AppSettings()
    settings.simulation.random_seed = 123
    settings.simulation.initial_agents = 10

    world_a = World.create(
                settings=settings,
                content=world.content,
                event_bus=world.event_bus,
                services=world.services,
                scenario=world.scenario,
            )
    world_b = World.create(
                settings=settings,
                content=world.content,
                event_bus=world.event_bus,
                services=world.services,
                scenario=world.scenario,
            )

    assert world_a.world_size == world_b.world_size
    assert world_a.state.resources == world_b.state.resources
    assert len(world_a.agent_ids) == len(world_b.agent_ids)
    assert world_a.to_dict()["state"]["temperature"] == world_b.to_dict()["state"]["temperature"]
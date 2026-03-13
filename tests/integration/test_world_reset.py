import pytest

from app.settings import AppSettings
from sim.world import World


@pytest.mark.integration
def test_reset_restores_initial_world_shape(world) -> None:
    settings = AppSettings()
    settings.simulation.initial_agents = 10

    world = World.create(
                settings=settings,
                content=world.content,
                event_bus=world.event_bus,
                services=world.services,
                scenario=world.scenario,
            )
    initial_agent_count = len(world.agent_ids)

    for _ in range(3):
        world.tick()

    world.reset()

    assert world.step_count == 0
    assert len(world.agent_ids) == initial_agent_count
    assert len(world.metrics.history) == 0
    assert len(world.replay.data.snapshots) >= 1
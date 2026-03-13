import pytest

from app.settings import AppSettings
from sim.world import World


@pytest.mark.integration
def test_simulation_smoke(world) -> None:
    settings = AppSettings()
    settings.simulation.initial_agents = 8

    world = World.create(
                settings=settings,
                content=world.content,
                event_bus=world.event_bus,
                services=world.services,
                scenario=world.scenario,
            )

    for _ in range(10):
        world.tick()

    assert world.step_count == 10
    assert len(world.metrics.history) == 10
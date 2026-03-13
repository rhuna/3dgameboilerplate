import pytest

from app.settings import AppSettings
from sim.world import World


@pytest.mark.integration
def test_step_real_time_advances_multiple_steps(world) -> None:
    settings = AppSettings()
    settings.simulation.sim_hz = 10

    world = World.create(
                settings=settings,
                content=world.content,
                event_bus=world.event_bus,
                services=world.services,
                scenario=world.scenario,
            )

    steps = world.step_real_time(0.5)

    assert steps == 5
    assert world.step_count == 5
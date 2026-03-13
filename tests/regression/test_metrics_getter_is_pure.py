import pytest

from app.settings import AppSettings
from sim.world import World


@pytest.mark.regression
def test_get_metrics_does_not_advance_simulation(world) -> None:
    settings = AppSettings()
    world = World.create(
                settings=settings,
                content=world.content,
                event_bus=world.event_bus,
                services=world.services,
                scenario=world.scenario,
            )

    before = world.step_count
    _ = world.get_metrics()
    after = world.step_count

    assert after == before
import pytest

from app.settings import AppSettings
from sim.world import World


@pytest.mark.integration
def test_world_tick_advances_step_count(world) -> None:
    settings = AppSettings()
    world = World.create(
                settings=settings,
                content=world.content,
                event_bus=world.event_bus,
                services=world.services,
                scenario=world.scenario,
            )
    before = world.step_count
    world.tick()
    after = world.step_count

    assert after == before + 1


@pytest.mark.integration
def test_world_tick_advances_step_count(world: World) -> None:
    before = world.step_count
    world.tick()
    assert world.step_count == before + 1
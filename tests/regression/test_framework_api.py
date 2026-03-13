import pytest

from app.settings import AppSettings
from sim.commands import SetWeatherCommand
from sim.world import World


@pytest.mark.regression
def test_world_create_is_stable_entry_point() -> None:
    settings = AppSettings()
    world = World.create(settings=settings)

    assert world is not None
    assert world.step_count == 0


@pytest.mark.regression
def test_world_issue_command_updates_simulation(world) -> None:
    settings = AppSettings()
    world = World.create(
                settings=settings,
                content=world.content,
                event_bus=world.event_bus,
                services=world.services,
                scenario=world.scenario,
            )

    world.issue_command(SetWeatherCommand(weather="rain"))

    assert world.settings.simulation.weather == "rain"


@pytest.mark.regression
def test_world_public_api_methods_exist() -> None:
    settings = AppSettings()
    world = World.create(settings=settings)

    assert callable(world.reset)
    assert callable(world.tick)
    assert callable(world.step_real_time)
    assert callable(world.get_metrics)
    assert callable(world.issue_command)
    assert callable(world.save)
    assert callable(world.load)
    assert callable(world.save_replay)
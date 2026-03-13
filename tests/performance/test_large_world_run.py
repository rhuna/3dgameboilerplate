from time import perf_counter

import pytest

from app.settings import AppSettings
from sim.world import World


@pytest.mark.performance
def test_large_run_completes_within_reasonable_time(world) -> None:
    settings = AppSettings()
    settings.simulation.world_size = 128
    settings.simulation.initial_agents = 250

    world = World.create(
                settings=settings,
                content=world.content,
                event_bus=world.event_bus,
                services=world.services,
                scenario=world.scenario,
            )

    start = perf_counter()

    for _ in range(200):
        world.tick()

    elapsed = perf_counter() - start

    assert world.step_count == 200
    assert elapsed < 10.0
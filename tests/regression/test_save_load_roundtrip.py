import pytest

from app.settings import AppSettings
from sim.world import World


@pytest.mark.regression
def test_save_load_roundtrip_preserves_world_state(tmp_path) -> None:
    settings = AppSettings()
    settings.simulation.initial_agents = 12

    world_a = World.create(
                settings=settings,
                content=None,
                event_bus=None,
                services=None,
                scenario=None
            )

    for _ in range(5):
        world_a.tick()

    save_path = tmp_path / "world_snapshot.json"
    world_a.save(save_path)

    world_b = World.create(
                settings=settings,
                content=None,
                event_bus=None,
                services=None,
                scenario=None,
            )
    world_b.load(save_path)

    assert world_b.step_count == world_a.step_count
    assert world_b.world_size == world_a.world_size
    assert world_b.state.resources == world_a.state.resources
    assert world_b.state.metrics == world_a.state.metrics
    assert len(world_b.agent_ids) == len(world_a.agent_ids)
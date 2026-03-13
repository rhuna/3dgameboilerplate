import pytest

from app.settings import AppSettings
from sim.replay.io import load_replay
from sim.world import World


@pytest.mark.regression
def test_replay_file_roundtrip(tmp_path) -> None:
    settings = AppSettings()
    world = World.create(
                settings=settings,
                content=None,
                event_bus=None,
                services=None,
                scenario=None,
            )

    for _ in range(5):
        world.tick()

    replay_path = tmp_path / "replay.json"
    world.save_replay(replay_path)

    replay = load_replay(replay_path)

    assert replay.seed == settings.simulation.random_seed
    assert replay.world_size == settings.simulation.world_size
    assert len(replay.snapshots) >= 1
    assert len(replay.events) >= 1
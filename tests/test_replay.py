from app.settings import AppSettings
from sim.replay.io import load_replay
from sim.world import World
from game.definitions.registry import ContentRegistry
from pathlib import Path


def test_world_can_save_replay(tmp_path: Path, content=ContentRegistry.load_defaults(), event_bus=None, services=None, scenario=None) -> None:
    settings = AppSettings()
    settings.simulation.initial_agents = 10

    world = World.create(
                settings=settings,
                content=content,
                event_bus=event_bus,
                services=services,
                scenario=scenario,
            )
    world.tick()
    world.tick()

    replay_path = tmp_path / "test_replay.json"
    world.save_replay(replay_path)

    replay = load_replay(replay_path)

    assert replay.seed == settings.simulation.random_seed
    assert replay.world_size == settings.simulation.world_size
    assert replay.sim_hz == settings.simulation.sim_hz
    assert len(replay.events) >= 1
    assert len(replay.snapshots) >= 1
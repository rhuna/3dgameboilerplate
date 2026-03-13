from pathlib import Path

from app.settings import AppSettings
from game.definitions.registry import ContentRegistry
from sim.components.agent_tag import AgentTag
from sim.components.transform import Transform
from sim.world import World

def snapshot(world: World) -> dict:
    ecs = world.ecs
    entities = sorted(list(ecs.entities.all_entities()))

    entity_data = []
    for entity_id in entities:
        transform = ecs.components.get(entity_id, Transform)
        tag = ecs.components.get(entity_id, AgentTag)

        entity_data.append(
            {
                "entity_id": entity_id,
                "x": round(transform.x, 6) if transform else None,
                "y": round(transform.y, 6) if transform else None,
                "archetype": tag.archetype if tag else None,
                "role": tag.role if tag else None,
            }
        )

    return {
        "sim_time": round(world.clock.sim_time, 6),
        "step_count": world.clock.step_count,
        "metrics": dict(world.state.metrics),
        "resources": dict(world.state.resources),
        "entities": entity_data,
    }

def test_same_seed_produces_same_initial_world() -> None:
    settings = AppSettings()
    settings.simulation.random_seed = 123
    settings.simulation.initial_agents = 10

    content = ContentRegistry.load_defaults()
    world_a = World(settings, content=content)
    world_b = World(settings, content=content)

    assert snapshot(world_a) == snapshot(world_b)


def test_reset_recreates_same_world_for_same_seed() -> None:
    settings = AppSettings()
    settings.simulation.random_seed = 123
    settings.simulation.initial_agents = 10

    world = World(settings)
    initial = snapshot(world)

    world.tick()
    world.tick()
    world.tick()

    world.reset()
    after_reset = snapshot(world)

    assert initial == after_reset



def test_ecs_save_load_round_trip(tmp_path: Path) -> None:
    settings = AppSettings()
    content = ContentRegistry.load_defaults()

    world = World(settings, content=content)
    for _ in range(10):
        world.tick()

    before = snapshot(world)

    save_path = tmp_path / "ecs_save.json"
    world.save(save_path)

    loaded_world = World(settings, content=content)
    loaded_world.load(save_path)

    after = snapshot(loaded_world)

    assert before == after

def test_agent_count_comes_from_ecs() -> None:
    settings = AppSettings()
    settings.simulation.initial_agents = 10

    world = World.create(settings, content=ContentRegistry.load_defaults(), event_bus=None, services=None, scenario=None)

    ecs_agent_count = len(world.ecs.query.entities_with(AgentTag))
    metric_agent_count = int(world.state.metrics.get("agent_count", 0))

    assert ecs_agent_count == metric_agent_count
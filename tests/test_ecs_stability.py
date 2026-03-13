# tests/test_ecs_stability.py
import gc
import pytest


class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Velocity:
    def __init__(self, dx=0, dy=0):
        self.dx = dx
        self.dy = dy


class Health:
    def __init__(self, hp=100):
        self.hp = hp


def as_set(result):
    return set(result)


def test_entity_creation_works(world):
    e1 = world.create_entity()
    e2 = world.create_entity()
    e3 = world.create_entity()

    assert e1 != e2 != e3
    assert e1 in world.entities
    assert e2 in world.entities
    assert e3 in world.entities


def test_component_add_remove_works(world):
    e = world.create_entity()

    world.add_component(e, Position(1, 2))
    assert e in as_set(world.query(Position))

    world.add_component(e, Velocity(3, 4))
    assert e in as_set(world.query(Position, Velocity))

    world.remove_component(e, Velocity)
    assert e not in as_set(world.query(Position, Velocity))
    assert e in as_set(world.query(Position))


def test_queries_return_correct_entity_sets(world):
    e1 = world.create_entity()
    e2 = world.create_entity()
    e3 = world.create_entity()
    e4 = world.create_entity()
    e5 = world.create_entity()

    world.add_component(e1, Position())
    world.add_component(e2, Position())
    world.add_component(e2, Velocity())
    world.add_component(e3, Health())
    world.add_component(e4, Position())
    world.add_component(e4, Health())
    world.add_component(e5, Position())
    world.add_component(e5, Velocity())
    world.add_component(e5, Health())

    assert as_set(world.query(Position)) == {e1, e2, e4, e5}
    assert as_set(world.query(Velocity)) == {e2, e5}
    assert as_set(world.query(Health)) == {e3, e4, e5}
    assert as_set(world.query(Position, Velocity)) == {e2, e5}
    assert as_set(world.query(Position, Health)) == {e4, e5}
    assert as_set(world.query(Position, Velocity, Health)) == {e5}

    world.remove_component(e5, Velocity)

    assert as_set(world.query(Position, Velocity)) == {e2}
    assert as_set(world.query(Position, Health)) == {e4, e5}
    assert as_set(world.query(Position, Velocity, Health)) == set()


def test_destroyed_entities_leave_queries(world):
    e = world.create_entity()
    world.add_component(e, Position())

    assert e in as_set(world.query(Position))

    world.destroy_entity(e)

    assert e not in as_set(world.query(Position))
    assert e not in world.entities


def test_repeated_mutations_remain_stable(world):
    entities = [world.create_entity() for _ in range(100)]

    for e in entities:
        world.add_component(e, Position())

    for i, e in enumerate(entities):
        if i % 2 == 0:
            world.add_component(e, Velocity())

    expected = {e for i, e in enumerate(entities) if i % 2 == 0}
    assert as_set(world.query(Position, Velocity)) == expected

    for i, e in enumerate(entities):
        if i % 4 == 0:
            world.remove_component(e, Velocity)

    expected = {e for i, e in enumerate(entities) if i % 2 == 0 and i % 4 != 0}
    assert as_set(world.query(Position, Velocity)) == expected


def test_no_unbounded_growth_after_create_destroy_cycles(world):
    def snapshot():
        return {
            "entity_count": len(world.entities),
            # Add your ECS internals here:
            # "position_store": len(world._components[Position]),
            # "velocity_store": len(world._components[Velocity]),
            # "query_cache": len(world._query_cache),
        }

    baseline = snapshot()

    for _ in range(50):
        batch = [world.create_entity() for _ in range(200)]
        for e in batch:
            world.add_component(e, Position())
            world.add_component(e, Velocity())
        for e in batch:
            world.remove_component(e, Velocity)
            world.destroy_entity(e)

    gc.collect()
    after = snapshot()

    assert after["entity_count"] == baseline["entity_count"]
    # Add similar assertions for component stores and caches.

def test_query_result_does_not_change_during_iteration(world):
        e1 = world.create_entity()
        e2 = world.create_entity()

        world.add_component(e1, Position())
        world.add_component(e2, Position())

        result = list(world.query(Position))

        for e in result:
            world.remove_component(e, Position)

        assert as_set(result) == {e1, e2}
        assert as_set(world.query(Position)) == set()
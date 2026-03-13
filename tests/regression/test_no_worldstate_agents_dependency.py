import pytest

from app.settings import AppSettings
from sim.world import World


@pytest.mark.regression
def test_worldstate_has_no_agents_list() -> None:
    world = World.create(settings=AppSettings())
    assert not hasattr(world.state, "agents")
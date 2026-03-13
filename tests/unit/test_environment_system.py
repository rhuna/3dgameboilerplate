import numpy as np
import pytest

from sim.state import WorldState
from sim.systems.environment_system import EnvironmentSystem


@pytest.mark.unit
def test_seed_temperature_initializes_grid() -> None:
    size = 8
    state = WorldState.create(size=size)
    system = EnvironmentSystem(size)

    system.seed_temperature(state.temperature, base=0.25, weather="clear")

    assert state.temperature.shape == (size, size)
    assert np.all(state.temperature >= 0.0)
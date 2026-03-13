import pytest

from app.settings import AppSettings
from sim.world import World


@pytest.mark.unit
def test_metrics_system_populates_metrics_dict(content,event_bus,services,scenario) -> None:
    settings = AppSettings()
    world = World.create(
                settings=settings,
                content=content,
                event_bus=event_bus,
                services=services,
                scenario=scenario,
            )

    world.metrics_system.update(world)

    metrics = world.state.metrics

    assert "avg_temperature" in metrics
    assert "agent_count" in metrics
    assert "resource_total" in metrics
    assert "agent_productivity" in metrics
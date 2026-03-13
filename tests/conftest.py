import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.settings import AppSettings
from game.definitions.registry import ContentRegistry
from sim.world import World


class DummyEventBus:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def emit(self, event_name: str, payload: dict) -> None:
        self.events.append((event_name, payload))


class DummyServices:
    def __init__(self) -> None:
        self._services: dict[str, object] = {}

    def set(self, key: str, value: object) -> None:
        self._services[key] = value

    def get(self, key: str, default: object | None = None) -> object | None:
        return self._services.get(key, default)


@pytest.fixture
def settings() -> AppSettings:
    s = AppSettings()
    s.simulation.random_seed = 7
    s.simulation.initial_agents = 10
    s.simulation.world_size = 32
    s.simulation.sim_hz = 30
    s.simulation.weather = "clear"
    return s


@pytest.fixture
def content():
    return ContentRegistry.load_defaults()


@pytest.fixture
def event_bus() -> DummyEventBus:
    return DummyEventBus()


@pytest.fixture
def services() -> DummyServices:
    return DummyServices()


@pytest.fixture
def scenario():
    return None


@pytest.fixture
def world(settings: AppSettings, content, event_bus: DummyEventBus, services: DummyServices, scenario) -> World:
    return World.create(
        settings=settings,
        content=content,
        event_bus=event_bus,
        services=services,
        scenario=scenario,
    )
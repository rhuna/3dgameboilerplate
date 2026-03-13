from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Command:
    pass


@dataclass(slots=True)
class SpawnEntityCommand(Command):
    archetype: str
    x: float
    y: float


@dataclass(slots=True)
class SetWeatherCommand(Command):
    weather: str
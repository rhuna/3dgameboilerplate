from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class SimSystem(Protocol):
    name: str

    def update(self, world) -> None:
        ...
        

@dataclass
class SystemScheduler:
    systems: list[SimSystem] = field(default_factory=list)

    def add(self, system: SimSystem) -> None:
        self.systems.append(system)

    def clear(self) -> None:
        self.systems.clear()

    def names(self) -> list[str]:
        return [getattr(system, "name", system.__class__.__name__) for system in self.systems]


    def run(self, world) -> None:
        for system in self.systems:
            system.update(world)
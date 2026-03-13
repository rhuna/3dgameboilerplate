from __future__ import annotations

from typing import Any, Type


class Query:
    def __init__(self, ecs_world) -> None:
        self.ecs_world = ecs_world

    def entities_with(self, *component_types: Type[Any]) -> set[int]:
        return self.ecs_world.components.entities_with(*component_types)
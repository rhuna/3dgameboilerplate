from __future__ import annotations

from collections import defaultdict
from typing import Any, Type


class ComponentStore:
    def __init__(self) -> None:
        self._stores: dict[Type[Any], dict[int, Any]] = defaultdict(dict)

    def add(self, entity_id: int, component: Any) -> None:
        self._stores[type(component)][entity_id] = component

    def remove(self, entity_id: int, component_type: Type[Any]) -> None:
        if component_type in self._stores:
            self._stores[component_type].pop(entity_id, None)

    def get(self, entity_id: int, component_type: Type[Any]) -> Any | None:
        return self._stores.get(component_type, {}).get(entity_id)

    def get_required(self, entity_id: int, component_type: Type[Any]) -> Any:
        component = self.get(entity_id, component_type)
        if component is None:
            raise KeyError(f"Entity {entity_id} missing component {component_type.__name__}")
        return component

    def has(self, entity_id: int, component_type: Type[Any]) -> bool:
        return entity_id in self._stores.get(component_type, {})

    def entities_with(self, *component_types: Type[Any]) -> set[int]:
        if not component_types:
            return set()

        sets = []
        for component_type in component_types:
            entities = set(self._stores.get(component_type, {}).keys())
            sets.append(entities)

        return set.intersection(*sets) if sets else set()

    def destroy_entity(self, entity_id: int) -> None:
        for store in self._stores.values():
            store.pop(entity_id, None)
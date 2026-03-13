from __future__ import annotations


class EntityManager:
    def __init__(self) -> None:
        self._next_entity_id = 0
        self._alive: set[int] = set()

    def create(self) -> int:
        entity_id = self._next_entity_id
        self._next_entity_id += 1
        self._alive.add(entity_id)
        return entity_id

    def destroy(self, entity_id: int) -> None:
        self._alive.discard(entity_id)

    def exists(self, entity_id: int) -> bool:
        return entity_id in self._alive

    def all_entities(self) -> set[int]:
        return set(self._alive)
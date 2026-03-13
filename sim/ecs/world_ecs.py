from __future__ import annotations

from sim.ecs.component_store import ComponentStore
from sim.ecs.entity_manager import EntityManager
from sim.ecs.query import Query


class ECSWorld:
    def __init__(self) -> None:
        self.entities = EntityManager()
        self.components = ComponentStore()
        self.query = Query(self)

    def create_entity(self) -> int:
        return self.entities.create()

    def destroy_entity(self, entity_id: int) -> None:
        self.components.destroy_entity(entity_id)
        self.entities.destroy(entity_id)
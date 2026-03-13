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

    # Compatibility helpers for tests / world code
    def add_component(self, entity_id: int, component: object) -> None:
        self.components.add(entity_id, component)

    def remove_component(self, entity_id: int, component_type: type) -> None:
        self.components.remove(entity_id, component_type)

    def get_component(self, entity_id: int, component_type: type):
        return self.components.get(entity_id, component_type)

    def has_component(self, entity_id: int, component_type: type) -> bool:
        return self.components.get(entity_id, component_type) is not None

    def query_entities(self, *component_types: type):
        return self.components.entities_with(*component_types)

    def query_iter(self, *component_types: type):
        return iter(sorted(self.components.entities_with(*component_types)))
from __future__ import annotations

from sim.components.health import Health


class DeathSystem:
    name = "death_system"

    def update(self, world) -> None:
        ecs = world.ecs
        dead_entities: list[int] = []

        for entity_id in ecs.query.entities_with(Health):
            health = ecs.components.get_required(entity_id, Health)
            if health.current <= 0:
                dead_entities.append(entity_id)

        for entity_id in dead_entities:
            if world.event_bus is not None:
                world.event_bus.emit("entity_died", {"entity_id": entity_id})
            ecs.destroy_entity(entity_id)
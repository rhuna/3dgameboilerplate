from __future__ import annotations

import math
from dataclasses import dataclass

from sim.components.combat_stats import CombatStats
from sim.components.cooldowns import Cooldowns
from sim.components.enemy_tag import EnemyTag
from sim.components.health import Health
from sim.components.mana import Mana
from sim.components.player_tag import PlayerTag
from sim.components.transform import Transform


@dataclass
class SpellCastRequest:
    caster_id: int
    spell_id: str
    target_x: float
    target_y: float


class CombatSystem:
    name = "combat_system"

    def __init__(self) -> None:
        self._cast_requests: list[SpellCastRequest] = []

    def queue_cast(self, caster_id: int, spell_id: str, target_x: float, target_y: float) -> None:
        self._cast_requests.append(
            SpellCastRequest(
                caster_id=caster_id,
                spell_id=spell_id,
                target_x=target_x,
                target_y=target_y,
            )
        )

    def update(self, world) -> None:
        self._resolve_spell_casts(world)
        self._resolve_enemy_melee(world)

    def _resolve_spell_casts(self, world) -> None:
        requests = self._cast_requests
        self._cast_requests = []

        for request in requests:
            self._resolve_spell_cast(world, request)

    def _resolve_spell_cast(self, world, request: SpellCastRequest) -> None:
        ecs = world.ecs
        spell = world.content.get_spell(request.spell_id)

        caster_transform = ecs.components.get(request.caster_id, Transform)
        caster_mana = ecs.components.get(request.caster_id, Mana)
        cooldowns = ecs.components.get(request.caster_id, Cooldowns)
        combat_stats = ecs.components.get(request.caster_id, CombatStats)

        if caster_transform is None or caster_mana is None or cooldowns is None:
            return

        if cooldowns.timers.get(request.spell_id, 0.0) > 0.0:
            return

        mana_cost = float(spell.get("mana_cost", 0.0))
        if caster_mana.current < mana_cost:
            return

        range_limit = float(spell.get("range", 10.0))
        base_damage = float(spell.get("damage", 0.0))
        spell_power = 1.0 if combat_stats is None else float(combat_stats.spell_power)
        damage = base_damage * spell_power

        target_id = None
        best_score = None

        for entity_id in ecs.query.entities_with(EnemyTag, Transform, Health):
            target_transform = ecs.components.get_required(entity_id, Transform)
            target_health = ecs.components.get_required(entity_id, Health)

            if target_health.current <= 0.0:
                continue

            dx_from_caster = target_transform.x - caster_transform.x
            dy_from_caster = target_transform.y - caster_transform.y
            distance_from_caster = math.hypot(dx_from_caster, dy_from_caster)

            if distance_from_caster > range_limit:
                continue

            # Prefer targets near the clicked point if targeting exists later.
            dx_from_click = target_transform.x - request.target_x
            dy_from_click = target_transform.y - request.target_y
            click_score = math.hypot(dx_from_click, dy_from_click)

            if best_score is None or click_score < best_score:
                best_score = click_score
                target_id = entity_id

        if target_id is None:
            return

        target_health = ecs.components.get_required(target_id, Health)

        caster_mana.current -= mana_cost
        cooldowns.timers[request.spell_id] = float(spell.get("cooldown", 0.5))
        target_health.current -= damage

        cast_payload = {
            "caster_id": request.caster_id,
            "target_id": target_id,
            "spell_id": request.spell_id,
            "damage": damage,
        }
        world.replay.record_event(world.step_count, "spell_cast", cast_payload)
        if world.event_bus is not None:
            world.event_bus.emit("spell_cast", cast_payload)

    def _resolve_enemy_melee(self, world) -> None:
        ecs = world.ecs
        player_id = world.find_player_id()
        if player_id is None:
            return

        player_transform = ecs.components.get(player_id, Transform)
        player_health = ecs.components.get(player_id, Health)
        if player_transform is None or player_health is None:
            return

        for enemy_id in ecs.query.entities_with(EnemyTag, Transform, Health, CombatStats, Cooldowns):
            enemy_transform = ecs.components.get_required(enemy_id, Transform)
            enemy_health = ecs.components.get_required(enemy_id, Health)
            combat_stats = ecs.components.get_required(enemy_id, CombatStats)
            cooldowns = ecs.components.get_required(enemy_id, Cooldowns)

            if enemy_health.current <= 0.0:
                continue

            cooldown_key = "enemy_basic_attack"
            if cooldowns.timers.get(cooldown_key, 0.0) > 0.0:
                continue

            dx = player_transform.x - enemy_transform.x
            dy = player_transform.y - enemy_transform.y
            distance = math.hypot(dx, dy)

            if distance > combat_stats.attack_range:
                continue

            player_health.current -= combat_stats.attack_damage
            cooldowns.timers[cooldown_key] = combat_stats.attack_cooldown

            hit_payload = {
                "attacker_id": enemy_id,
                "target_id": player_id,
                "damage": combat_stats.attack_damage,
            }
            world.replay.record_event(world.step_count, "enemy_attack", hit_payload)
            if world.event_bus is not None:
                world.event_bus.emit("enemy_attack", hit_payload)
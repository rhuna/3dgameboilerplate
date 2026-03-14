from __future__ import annotations

import math

from game.gameplay.commands import (
    CastSpellCommand,
    DodgeCommand,
    InteractCommand,
    MovePlayerCommand,
    SelectSpellCommand,
)
from sim.components.facing import Facing
from sim.components.move_intent import MoveIntent
from sim.components.movement import Movement
from sim.components.spellbook import Spellbook
from sim.components.transform import Transform


class PlayerControllerSystem:
    name = "player_controller_system"

    def update(self, world) -> None:
        # Player commands are handled immediately through handle_command().
        return

    def handle_command(self, world, command: object) -> bool:
        if isinstance(command, MovePlayerCommand):
            self._handle_move_player(world, command)
            return True

        if isinstance(command, CastSpellCommand):
            self._handle_cast_spell(world, command)
            return True

        if isinstance(command, SelectSpellCommand):
            self._handle_select_spell(world, command)
            return True

        if isinstance(command, InteractCommand):
            self._handle_interact(world, command)
            return True

        if isinstance(command, DodgeCommand):
            self._handle_dodge(world, command)
            return True

        return False

    def _handle_move_player(self, world, command: MovePlayerCommand) -> None:
        player_id = world.find_player_id()
        if player_id is None:
            return

        transform = world.ecs.components.get(player_id, Transform)
        movement = world.ecs.components.get(player_id, Movement)
        move_intent = world.ecs.components.get(player_id, MoveIntent)
        facing = world.ecs.components.get(player_id, Facing)

        if transform is None or movement is None:
            return

        length = math.hypot(command.move_x, command.move_y)
        if length <= 0.0:
            if move_intent is not None:
                move_intent.x = 0.0
                move_intent.y = 0.0
            return

        dir_x = command.move_x / length
        dir_y = command.move_y / length

        if move_intent is not None:
            move_intent.x = dir_x
            move_intent.y = dir_y

        if facing is not None:
            facing.x = dir_x
            facing.y = dir_y

        distance_multiplier = 10.0 if command.run else 6.0
        target_distance = max(1.0, movement.speed * world.fixed_dt * distance_multiplier)
        entity_radius = 0.5

        movement.target_x = max(
            entity_radius,
            min(world.world_size - entity_radius, transform.x + dir_x * target_distance),
        )
        movement.target_y = max(
            entity_radius,
            min(world.world_size - entity_radius, transform.y + dir_y * target_distance),
        )

    def _handle_cast_spell(self, world, command: CastSpellCommand) -> None:
        world.combat_system.queue_cast(
            caster_id=command.caster_id,
            spell_id=command.spell_id,
            target_x=command.target_x,
            target_y=command.target_y,
        )

    def _handle_select_spell(self, world, command: SelectSpellCommand) -> None:
        player_id = world.find_player_id()
        if player_id is None:
            return

        spellbook = world.ecs.components.get(player_id, Spellbook)
        if spellbook is None or not spellbook.slots:
            return

        spellbook.selected_index = max(0, min(command.slot, len(spellbook.slots) - 1))

    def _handle_interact(self, world, command: InteractCommand) -> None:
        interact_payload = {
            "actor_id": command.actor_id,
            "step_count": world.step_count,
        }
        world.replay.record_event(world.step_count, "interact_requested", interact_payload)
        if world.event_bus is not None:
            world.event_bus.emit("interact_requested", interact_payload)

    def _handle_dodge(self, world, command: DodgeCommand) -> None:
        transform = world.ecs.components.get(command.actor_id, Transform)
        movement = world.ecs.components.get(command.actor_id, Movement)
        facing = world.ecs.components.get(command.actor_id, Facing)

        if transform is None or movement is None:
            return

        dash_x = 0.0
        dash_y = 1.0
        if facing is not None:
            dash_x = facing.x
            dash_y = facing.y

        length = math.hypot(dash_x, dash_y)
        if length > 1e-6:
            dash_x /= length
            dash_y /= length
        else:
            dash_x, dash_y = 0.0, 1.0

        dash_distance = 2.5
        entity_radius = 0.5

        movement.target_x = max(
            entity_radius,
            min(world.world_size - entity_radius, transform.x + dash_x * dash_distance),
        )
        movement.target_y = max(
            entity_radius,
            min(world.world_size - entity_radius, transform.y + dash_y * dash_distance),
        )

        dodge_payload = {
            "actor_id": command.actor_id,
            "x": movement.target_x,
            "y": movement.target_y,
        }
        world.replay.record_event(world.step_count, "dodge_requested", dodge_payload)
        if world.event_bus is not None:
            world.event_bus.emit("dodge_requested", dodge_payload)
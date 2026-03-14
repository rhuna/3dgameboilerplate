from __future__ import annotations

from game.gameplay.commands import (
    CastSpellCommand,
    DodgeCommand,
    InteractCommand,
    MovePlayerCommand,
    SelectSpellCommand,
)


class InputToCommandsAdapter:
    """
    Translate raw input state into gameplay command dataclasses.

    InputState currently only exposes keys_down, so this adapter performs
    edge detection to derive "just pressed" actions.
    """

    def __init__(self, input_state, world) -> None:
        self.input_state = input_state
        self.world = world
        self._previous_keys_down: set[str] = set()

    def get_commands(self) -> list[object]:
        commands: list[object] = []

        keys_down = set(self.input_state.keys_down)
        just_pressed = keys_down - self._previous_keys_down

        player_id = self.world.find_player_id()

        # ------------------------------------------
        # Continuous movement: WASD
        # ------------------------------------------
        move_x = 0.0
        move_y = 0.0

        if "w" in keys_down:
            move_y += 1.0
        if "s" in keys_down:
            move_y -= 1.0
        if "a" in keys_down:
            move_x -= 1.0
        if "d" in keys_down:
            move_x += 1.0

        run_held = "shift" in keys_down

        if move_x != 0.0 or move_y != 0.0:
            commands.append(
                MovePlayerCommand(
                    move_x=move_x,
                    move_y=move_y,
                    run=run_held,
                )
            )

        # ------------------------------------------
        # Discrete actions: interact / dodge
        # ------------------------------------------
        if player_id is not None:
            if "e" in just_pressed:
                commands.append(InteractCommand(actor_id=player_id))

            if "shift" in just_pressed:
                commands.append(DodgeCommand(actor_id=player_id))

        # ------------------------------------------
        # Spell selection: number keys 1-9
        # ------------------------------------------
        for i in range(1, 10):
            key = str(i)
            if key in just_pressed:
                commands.append(SelectSpellCommand(slot=i - 1))
                break

        # ------------------------------------------
        # Spell cast: left mouse click
        # ------------------------------------------
        if "mouse1" in just_pressed and player_id is not None:
            selected_spell = self.world.get_selected_spell(player_id)

            commands.append(
                CastSpellCommand(
                    spell_id=selected_spell,
                    caster_id=player_id,
                    target_x=0.0,
                    target_y=0.0,
                )
            )

        self._previous_keys_down = keys_down
        return commands
from __future__ import annotations

import math

from game.gameplay.commands import MovePlayerCommand


class InputToCommandsAdapter:
    def __init__(self, input_state):
        self.input_state = input_state

    def get_commands(self):
        commands = []

        move_x = 0.0
        move_y = 0.0

        if self.input_state.is_down("w"):
            move_y += 1.0
        if self.input_state.is_down("s"):
            move_y -= 1.0
        if self.input_state.is_down("a"):
            move_x -= 1.0
        if self.input_state.is_down("d"):
            move_x += 1.0

        length = math.hypot(move_x, move_y)
        if length > 0.0:
            move_x /= length
            move_y /= length
            commands.append(MovePlayerCommand(move_x=move_x, move_y=move_y))

        return commands
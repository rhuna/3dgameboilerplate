from __future__ import annotations

from collections import defaultdict
from typing import Callable

from sim.replay.models import ReplayCommand, ReplayData


class ReplayPlayer:
    def __init__(self, replay: ReplayData) -> None:
        self.replay = replay
        self._commands_by_step: dict[int, list[ReplayCommand]] = defaultdict(list)

        for command in replay.commands:
            self._commands_by_step[command.step].append(command)

    def play(
        self,
        world,
        *,
        apply_command: Callable[[object, ReplayCommand], None] | None = None,
        max_step: int | None = None,
    ) -> None:
        final_step = max_step if max_step is not None else self._infer_final_step()

        for _ in range(final_step):
            current_step = world.step_count

            for command in self._commands_by_step.get(current_step, []):
                if apply_command is not None:
                    apply_command(world, command)

            world.tick()

    def _infer_final_step(self) -> int:
        max_command_step = max((c.step for c in self.replay.commands), default=0)
        max_snapshot_step = max((s.step for s in self.replay.snapshots), default=0)
        max_event_step = max((e.step for e in self.replay.events), default=0)
        return max(max_command_step, max_snapshot_step, max_event_step)
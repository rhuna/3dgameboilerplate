from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class InputState:
    keys_down: set[str] = field(default_factory=set)
    mouse_held: bool = False
    debug_visible: bool = True
    paused: bool = False
    single_step_requested: bool = False
    sim_speed: float = 1.0

    def press(self, key: str) -> None:
        self.keys_down.add(key)

    def release(self, key: str) -> None:
        self.keys_down.discard(key)

    def is_down(self, key: str) -> bool:
        return key in self.keys_down

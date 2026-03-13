from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MovePlayerCommand:
    move_x: float
    move_y: float


@dataclass
class CastSpellCommand:
    spell_id: str
    caster_id: int
    target_x: float
    target_y: float
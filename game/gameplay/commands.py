from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MovePlayerCommand:
    move_x: float
    move_y: float
    run: bool = False


@dataclass
class CastSpellCommand:
    spell_id: str
    caster_id: int
    target_x: float
    target_y: float


@dataclass
class SelectSpellCommand:
    slot: int


@dataclass
class InteractCommand:
    actor_id: int


@dataclass
class DodgeCommand:
    actor_id: int
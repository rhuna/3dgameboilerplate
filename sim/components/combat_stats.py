from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class CombatStats:
    spell_power: float = 1.0
    aggro_range: float = 10.0
    attack_range: float = 2.0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CombatStats":
        return cls(**data)

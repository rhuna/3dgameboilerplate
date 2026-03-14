from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class CombatStats:
    spell_power: float = 1.0
    aggro_range: float = 12.0
    attack_range: float = 1.75
    attack_damage: float = 8.0
    attack_cooldown: float = 0.75

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CombatStats":
        return cls(**data)
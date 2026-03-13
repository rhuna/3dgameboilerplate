from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class Mana:
    current: float
    maximum: float

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Mana":
        return cls(**data)
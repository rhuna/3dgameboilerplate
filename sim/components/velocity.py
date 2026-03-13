from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class Velocity:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Velocity":
        return cls(**data)

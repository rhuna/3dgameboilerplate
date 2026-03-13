from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class Movement:
    speed: float
    target_x: float
    target_y: float

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Movement":
        return cls(**data)
from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class MoveIntent:
    x: float = 0.0
    y: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "MoveIntent":
        return cls(**data)

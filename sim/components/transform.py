from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class Transform:
    x: float
    y: float
    z: float = 0.0


    def to_dict(self) -> dict:
            return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Transform":
        return cls(**data)
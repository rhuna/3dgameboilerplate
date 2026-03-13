from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class Renderable:
    model_name: str
    color: tuple[float, float, float, float]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Renderable":
        return cls(**data)
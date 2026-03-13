from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class Health:
    current: float
    maximum: float

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Health":
        return cls(**data)
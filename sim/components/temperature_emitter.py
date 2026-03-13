from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class TemperatureEmitter:
    amount: float


    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TemperatureEmitter":
        return cls(**data)
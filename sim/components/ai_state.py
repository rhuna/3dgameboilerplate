from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class AIState:
    state: str = "idle"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AIState":
        return cls(**data)

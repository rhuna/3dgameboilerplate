from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class AgentTag:
    archetype: str
    role: str
    state: str = "idle"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AgentTag":
        return cls(**data)
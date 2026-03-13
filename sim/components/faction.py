from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class Faction:
    name: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Faction":
        return cls(**data)
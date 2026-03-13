from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class PlayerTag:
    name: str = "player"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "PlayerTag":
        return cls(**data)

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class EnemyTag:
    kind: str = "enemy"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "EnemyTag":
        return cls(**data)

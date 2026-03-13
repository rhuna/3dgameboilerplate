from __future__ import annotations

from dataclasses import dataclass, asdict, field


@dataclass
class Cooldowns:
    timers: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Cooldowns":
        return cls(**data)

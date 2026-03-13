from __future__ import annotations

from dataclasses import dataclass, asdict, field


@dataclass
class Spellbook:
    slots: list[str] = field(default_factory=lambda: ["fireball"])
    selected_index: int = 0

    @property
    def selected_spell(self) -> str:
        if not self.slots:
            return "fireball"
        index = max(0, min(self.selected_index, len(self.slots) - 1))
        return self.slots[index]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Spellbook":
        return cls(**data)

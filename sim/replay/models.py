from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class ReplayCommand:
    step: int
    command_type: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReplayCommand":
        return cls(
            step=int(data["step"]),
            command_type=str(data["command_type"]),
            payload=dict(data.get("payload", {})),
        )


@dataclass(slots=True)
class ReplayEvent:
    step: int
    event_type: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReplayEvent":
        return cls(
            step=int(data["step"]),
            event_type=str(data["event_type"]),
            payload=dict(data.get("payload", {})),
        )


@dataclass(slots=True)
class ReplaySnapshot:
    step: int
    world: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReplaySnapshot":
        return cls(
            step=int(data["step"]),
            world=dict(data["world"]),
        )


@dataclass(slots=True)
class ReplayData:
    replay_version: int
    sim_version: str
    seed: int
    world_size: int
    sim_hz: int
    scenario_name: str | None
    commands: list[ReplayCommand] = field(default_factory=list)
    events: list[ReplayEvent] = field(default_factory=list)
    snapshots: list[ReplaySnapshot] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "replay_version": self.replay_version,
            "sim_version": self.sim_version,
            "seed": self.seed,
            "world_size": self.world_size,
            "sim_hz": self.sim_hz,
            "scenario_name": self.scenario_name,
            "commands": [c.to_dict() for c in self.commands],
            "events": [e.to_dict() for e in self.events],
            "snapshots": [s.to_dict() for s in self.snapshots],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReplayData":
        return cls(
            replay_version=int(data["replay_version"]),
            sim_version=str(data.get("sim_version", "0.1.0")),
            seed=int(data["seed"]),
            world_size=int(data["world_size"]),
            sim_hz=int(data["sim_hz"]),
            scenario_name=data.get("scenario_name"),
            commands=[ReplayCommand.from_dict(x) for x in data.get("commands", [])],
            events=[ReplayEvent.from_dict(x) for x in data.get("events", [])],
            snapshots=[ReplaySnapshot.from_dict(x) for x in data.get("snapshots", [])],
            metadata=dict(data.get("metadata", {})),
        )
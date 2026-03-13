from __future__ import annotations

from typing import Any

from sim.replay.models import ReplayCommand, ReplayData, ReplayEvent, ReplaySnapshot


class ReplayRecorder:
    def __init__(
        self,
        *,
        sim_version: str,
        seed: int,
        world_size: int,
        sim_hz: int,
        scenario_name: str | None,
        snapshot_interval: int = 100,
    ) -> None:
        self.snapshot_interval = max(0, snapshot_interval)
        self.data = ReplayData(
            replay_version=1,
            sim_version=sim_version,
            seed=seed,
            world_size=world_size,
            sim_hz=sim_hz,
            scenario_name=scenario_name,
            metadata={},
        )

    def record_command(self, step: int, command_type: str, payload: dict[str, Any]) -> None:
        self.data.commands.append(
            ReplayCommand(
                step=step,
                command_type=command_type,
                payload=dict(payload),
            )
        )

    def record_event(self, step: int, event_type: str, payload: dict[str, Any]) -> None:
        self.data.events.append(
            ReplayEvent(
                step=step,
                event_type=event_type,
                payload=dict(payload),
            )
        )

    def maybe_record_snapshot(self, world: Any) -> None:
        if self.snapshot_interval <= 0:
            return

        if world.step_count % self.snapshot_interval != 0:
            return

        self.record_snapshot(world.step_count, world.to_dict())

    def record_snapshot(self, step: int, world_dict: dict[str, Any]) -> None:
        self.data.snapshots.append(
            ReplaySnapshot(
                step=step,
                world=world_dict,
            )
        )

    def attach_metadata(self, **kwargs: Any) -> None:
        self.data.metadata.update(kwargs)
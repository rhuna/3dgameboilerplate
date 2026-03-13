from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SimulationClock:
    fixed_dt: float
    accumulator: float = 0.0
    sim_time: float = 0.0
    step_count: int = 0
    max_substeps: int = 8

    def add_real_time(self, dt: float) -> int:
        self.accumulator += dt
        steps = 0

        while self.accumulator >= self.fixed_dt and steps < self.max_substeps:
            self.accumulator -= self.fixed_dt
            steps += 1

        return steps

    def advance_one_step(self) -> None:
        self.sim_time += self.fixed_dt
        self.step_count += 1

    def clear(self) -> None:
        self.accumulator = 0.0
        self.sim_time = 0.0
        self.step_count = 0

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np



@dataclass
class WorldState:
    size: int
    temperature: np.ndarray
    occupancy: np.ndarray
    metrics: dict[str, float] = field(default_factory=dict)
    resources: dict[str, float] = field(default_factory=dict)

    @classmethod
    def create(cls, size: int) -> "WorldState":
        temperature = np.zeros((size, size), dtype=np.float32)
        occupancy = np.zeros((size, size), dtype=np.int32)
        metrics: dict[str, float] = {}
        resources: dict[str, float] = {}

        return cls(
            size=size,
            temperature=temperature,
            occupancy=occupancy,
            metrics=metrics,
            resources=resources,
        )

    def to_dict(self) -> dict:
        return {
            "size": self.size,
            "temperature": self.temperature.tolist(),
            "occupancy": self.occupancy.tolist(),
            "metrics": self.metrics,
            "resources": self.resources,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorldState":
        size = data.get("size")
        temperature = np.array(data["temperature"], dtype=np.float32)
        occupancy_data = data.get("occupancy")

        if occupancy_data is None:
            if size is None:
                size = int(temperature.shape[0])
            occupancy = np.zeros((size, size), dtype=np.int32)
        else:
            occupancy = np.array(occupancy_data, dtype=np.int32)

        if size is None:
            size = int(temperature.shape[0])

        return cls(
            size=size,
            temperature=temperature,
            occupancy=occupancy,
            metrics=data.get("metrics", {}),
            resources=data.get("resources", {}),
        )
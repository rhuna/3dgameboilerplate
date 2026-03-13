from __future__ import annotations

from pathlib import Path
from typing import Any

import json
from pydantic import BaseModel, Field


class WindowSettings(BaseModel):
    width: int = 1280
    height: int = 720
    title: str = "FireWizard3D Simulation"
    fullscreen: bool = False


class SimulationSettings(BaseModel):
    sim_hz: int = 30
    max_frame_time: float = 0.25
    initial_agents: int = 25
    world_size: int = 64
    random_seed: int = 7
    temperature_base: float = 0.25
    weather: str = "clear"
    default_steps_headless: int = 1000

class CameraSettings(BaseModel):
    move_speed: float = 20.0
    zoom_speed: float = 5.0
    rotation_sensitivity: float = 0.2
    start_pos: tuple[float, float, float] = (0.0, -40.0, 25.0)
    look_at: tuple[float, float, float] = (0.0, 0.0, 0.0)


class AppSettings(BaseModel):
    window: WindowSettings = Field(default_factory=WindowSettings)
    simulation: SimulationSettings = Field(default_factory=SimulationSettings)
    camera: CameraSettings = Field(default_factory=CameraSettings)


DEFAULT_SETTINGS_PATH = Path(__file__).resolve().parents[1] / "data" / "configs" / "default_settings.json"


def load_settings(path: str | Path | None = None) -> AppSettings:
    settings_path = Path(path) if path else DEFAULT_SETTINGS_PATH
    if not settings_path.exists():
        return AppSettings()

    with settings_path.open("r", encoding="utf-8") as f:
        payload: dict[str, Any] = json.load(f)

    return AppSettings.model_validate(payload)

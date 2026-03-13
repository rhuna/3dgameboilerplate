from __future__ import annotations

from engine.scenes.base_scene import BaseScene
from engine.scene import SceneBuilder


class SimulationScene(BaseScene):
    def __init__(self, app) -> None:
        super().__init__(app)
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        SceneBuilder(self.app).build()
        self._loaded = True

    def activate(self) -> None:
        pass

    def deactivate(self) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def unload(self) -> None:
        self._loaded = False
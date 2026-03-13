from __future__ import annotations

from panda3d.core import AmbientLight, DirectionalLight, Vec4
from engine.events import EventBus

class SceneBuilder:
    def __init__(self, base) -> None:
        self.base = base

    def build(self) -> None:
        self.base.setBackgroundColor(0.08, 0.10, 0.14, 1.0)

        ambient = AmbientLight("ambient")
        ambient.setColor(Vec4(0.35, 0.35, 0.4, 1.0))
        ambient_np = self.base.render.attachNewNode(ambient)
        self.base.render.setLight(ambient_np)

        sun = DirectionalLight("sun")
        sun.setColor(Vec4(0.9, 0.9, 0.82, 1.0))
        sun_np = self.base.render.attachNewNode(sun)
        sun_np.setHpr(45, -60, 0)
        self.base.render.setLight(sun_np)
4       


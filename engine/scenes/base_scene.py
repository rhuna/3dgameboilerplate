from __future__ import annotations


class BaseScene:
    def __init__(self, app) -> None:
        self.app = app

    def load(self) -> None:
        pass

    def activate(self) -> None:
        pass

    def deactivate(self) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def unload(self) -> None:
        pass
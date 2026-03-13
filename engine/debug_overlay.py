from __future__ import annotations

from direct.gui.OnscreenText import OnscreenText


class DebugOverlay:
    def __init__(self, base) -> None:
        self.text = OnscreenText(
            text="",
            pos=(-1.32, 0.92),
            scale=0.05,
            align=0,
            mayChange=True,
            fg=(1, 1, 1, 1),
        )
        self.visible = True

    def set_text(self, value: str) -> None:
        self.text.setText(value)

    def set_visible(self, visible: bool) -> None:
        self.visible = visible
        if visible:
            self.text.show()
        else:
            self.text.hide()

    def toggle(self) -> None:
        self.set_visible(not self.visible)
from __future__ import annotations

import math

from panda3d.core import Vec3
from sim.components.transform import Transform


class CameraController:
    def __init__(self, base, settings, input_state) -> None:
        self.base = base
        self.settings = settings
        self.input_state = input_state

        self.target = Vec3(
            float(getattr(settings, "target_x", 20.0)),
            float(getattr(settings, "target_y", 20.0)),
            float(getattr(settings, "target_z", 0.0)),
        )

        self.distance = float(getattr(settings, "distance", 18.0))
        self.min_distance = float(getattr(settings, "min_distance", 6.0))
        self.max_distance = float(getattr(settings, "max_distance", 50.0))
        self.zoom_step = float(getattr(settings, "zoom_step", 2.0))

        self.yaw = float(getattr(settings, "yaw", 0.0))
        self.pitch = float(getattr(settings, "pitch", -30.0))
        self.height_offset = float(getattr(settings, "height_offset", 3.0))
        self.follow_smoothing = float(getattr(settings, "follow_smoothing", 10.0))

        self._apply_transform()

    def zoom(self, direction: float) -> None:
        self.distance += float(direction) * self.zoom_step
        self.distance = max(self.min_distance, min(self.max_distance, self.distance))
        self._apply_transform()

    def _apply_transform(self) -> None:
        pitch_rad = math.radians(self.pitch)
        yaw_rad = math.radians(self.yaw)

        x = self.target.x - self.distance * math.cos(pitch_rad) * math.sin(yaw_rad)
        y = self.target.y - self.distance * math.cos(pitch_rad) * math.cos(yaw_rad)
        z = self.target.z - self.distance * math.sin(pitch_rad)

        self.base.camera.setPos(x, y, z)
        self.base.camera.lookAt(self.target.x, self.target.y, self.target.z)

    def update(self, dt: float) -> None:
        adventure_mode = getattr(getattr(self.base, "scenario", None), "game_mode", "sandbox") == "adventure"

        if adventure_mode:
            player_id = self.base.world.find_player_id()

            if player_id is not None:
                transform = self.base.world.ecs.components.get(player_id, Transform)

                if transform is not None:
                    desired_target = Vec3(
                        float(transform.x),
                        float(transform.y),
                        float(transform.z + self.height_offset),
                    )

                    lerp_t = max(0.0, min(1.0, dt * self.follow_smoothing))
                    self.target = self.target * (1.0 - lerp_t) + desired_target * lerp_t

            if getattr(self.input_state, "mouse_held", False) and self.base.mouseWatcherNode.hasMouse():
                md = self.base.win.getPointer(0)
                center_x = self.base.win.getXSize() // 2
                center_y = self.base.win.getYSize() // 2
                dx = md.getX() - center_x
                dy = md.getY() - center_y

                rotation_sensitivity = float(getattr(self.settings, "rotation_sensitivity", 120.0))
                self.yaw -= dx * rotation_sensitivity * dt
                self.pitch = max(-75.0, min(-10.0, self.pitch - dy * rotation_sensitivity * dt))

                self.base.win.movePointer(0, center_x, center_y)

            self._apply_transform()
            return

        move_speed = float(getattr(self.settings, "move_speed", 20.0)) * dt

        if self.input_state.is_down("w"):
            self.target.y += move_speed
        if self.input_state.is_down("s"):
            self.target.y -= move_speed
        if self.input_state.is_down("a"):
            self.target.x -= move_speed
        if self.input_state.is_down("d"):
            self.target.x += move_speed
        if self.input_state.is_down("q"):
            self.target.z -= move_speed
        if self.input_state.is_down("e"):
            self.target.z += move_speed

        if getattr(self.input_state, "mouse_held", False) and self.base.mouseWatcherNode.hasMouse():
            md = self.base.win.getPointer(0)
            center_x = self.base.win.getXSize() // 2
            center_y = self.base.win.getYSize() // 2
            dx = md.getX() - center_x
            dy = md.getY() - center_y

            rotation_sensitivity = float(getattr(self.settings, "rotation_sensitivity", 120.0))
            self.yaw -= dx * rotation_sensitivity * dt
            self.pitch = max(-85.0, min(-5.0, self.pitch - dy * rotation_sensitivity * dt))

            self.base.win.movePointer(0, center_x, center_y)

        self._apply_transform()
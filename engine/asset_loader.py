from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from panda3d.core import NodePath


@dataclass
class AssetLoader:
    loader: Any

    model_manifest: dict[str, str] = field(default_factory=dict)
    texture_manifest: dict[str, str] = field(default_factory=dict)
    sound_manifest: dict[str, str] = field(default_factory=dict)

    model_cache: dict[str, NodePath] = field(default_factory=dict)
    texture_cache: dict[str, Any] = field(default_factory=dict)
    sound_cache: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.model_manifest:
            self.model_manifest = {
                "agent_default": "models/misc/sphere",
            }

        if not self.texture_manifest:
            self.texture_manifest = {}

        if not self.sound_manifest:
            self.sound_manifest = {}

    def register_model(self, logical_name: str, path: str) -> None:
        self.model_manifest[logical_name] = path

    def register_texture(self, logical_name: str, path: str) -> None:
        self.texture_manifest[logical_name] = path

    def register_sound(self, logical_name: str, path: str) -> None:
        self.sound_manifest[logical_name] = path

    def load_model(self, logical_name: str, parent: NodePath | None = None) -> NodePath | None:
        if logical_name in self.model_cache:
            return self._copy_model(self.model_cache[logical_name], parent)

        path = self.model_manifest.get(logical_name)
        if path is None:
            print(f"[AssetLoader] Missing model registration: {logical_name}")
            fallback = self._load_missing_model_fallback()
            if fallback is None:
                return None
            return self._copy_model(fallback, parent)

        try:
            model = self.loader.loadModel(path)
            if model is None or model.isEmpty():
                print(f"[AssetLoader] Failed to load model: {logical_name} -> {path}")
                fallback = self._load_missing_model_fallback()
                if fallback is None:
                    return None
                return self._copy_model(fallback, parent)

            self.model_cache[logical_name] = model
            return self._copy_model(model, parent)

        except Exception as exc:
            print(f"[AssetLoader] Error loading model '{logical_name}' from '{path}': {exc}")
            fallback = self._load_missing_model_fallback()
            if fallback is None:
                return None
            return self._copy_model(fallback, parent)

    def load_texture(self, logical_name: str):
        if logical_name in self.texture_cache:
            return self.texture_cache[logical_name]

        path = self.texture_manifest.get(logical_name)
        if path is None:
            print(f"[AssetLoader] Missing texture registration: {logical_name}")
            return None

        try:
            texture = self.loader.loadTexture(path)
            if texture is None:
                print(f"[AssetLoader] Failed to load texture: {logical_name} -> {path}")
                return None

            self.texture_cache[logical_name] = texture
            return texture

        except Exception as exc:
            print(f"[AssetLoader] Error loading texture '{logical_name}' from '{path}': {exc}")
            return None

    def load_sound(self, logical_name: str, base) -> Any | None:
        if logical_name in self.sound_cache:
            return self.sound_cache[logical_name]

        path = self.sound_manifest.get(logical_name)
        if path is None:
            print(f"[AssetLoader] Missing sound registration: {logical_name}")
            return None

        try:
            sound = base.loader.loadSfx(path)
            if sound is None:
                print(f"[AssetLoader] Failed to load sound: {logical_name} -> {path}")
                return None

            self.sound_cache[logical_name] = sound
            return sound

        except Exception as exc:
            print(f"[AssetLoader] Error loading sound '{logical_name}' from '{path}': {exc}")
            return None

    def _copy_model(self, model: NodePath, parent: NodePath | None = None) -> NodePath:
        if parent is not None:
            return model.copyTo(parent)

        temp_root = NodePath("asset_instance_root")
        copy = model.copyTo(temp_root)
        copy.wrtReparentTo(temp_root)
        return copy

    def _load_missing_model_fallback(self) -> NodePath | None:
        try:
            fallback = self.loader.loadModel("models/misc/sphere")
            if fallback is None or fallback.isEmpty():
                return None
            return fallback
        except Exception:
            return None
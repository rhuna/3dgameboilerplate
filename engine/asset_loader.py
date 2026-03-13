from __future__ import annotations

from panda3d.core import NodePath


class AssetLoader:
    def __init__(self, base) -> None:
        self.base = base

        # Game-facing model ids -> Panda3D model paths.
        # Replace these later with your real assets.
        self._model_registry: dict[str, str] = {
            "agent_default": "models/misc/rgbCube",
            "player_default": "models/misc/rgbCube",
            "enemy_default": "models/misc/rgbCube",
            "interactable_default": "models/misc/rgbCube",
        }

        self._warned_missing_models: set[str] = set()

    def register_model(self, model_name: str, model_path: str) -> None:
        self._model_registry[model_name] = model_path

    def has_model(self, model_name: str) -> bool:
        return model_name in self._model_registry

    def resolve_model_name(self, requested_name: str | None) -> str:
        if requested_name and requested_name in self._model_registry:
            return requested_name

        if requested_name and requested_name not in self._warned_missing_models:
            print(f"[AssetLoader] Missing model registration: {requested_name} -> using agent_default")
            self._warned_missing_models.add(requested_name)

        return "agent_default"

    def _load_model_path(self, model_path: str, parent: NodePath) -> NodePath:
        model = self.base.loadModel(model_path)
        if model.isEmpty():
            raise RuntimeError(f"Loaded empty model for path: {model_path}")
        return model

    def load_model(self, requested_name: str | None, parent: NodePath) -> NodePath:
        resolved_name = self.resolve_model_name(requested_name)
        model_path = self._model_registry[resolved_name]

        try:
            return self._load_model_path(model_path, parent)
        except Exception as exc:
            if model_path != "models/misc/rgbCube":
                print(
                    f"[AssetLoader] Failed to load '{model_path}' for '{resolved_name}': {exc}. "
                    "Using rgbCube fallback."
                )
            return self._load_model_path("models/misc/rgbCube", parent)

    def create_instance(self, requested_name: str | None, parent: NodePath) -> NodePath:
        model = self.load_model(requested_name, parent)
        return model.copyTo(parent)
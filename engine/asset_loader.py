from __future__ import annotations

from pathlib import Path

from panda3d.core import Filename, NodePath
from direct.actor.Actor import Actor
import json


class AssetLoader:
    def __init__(self, base) -> None:
        self.base = base
        self.project_root = Path(__file__).resolve().parents[1]
        self.assets_root = self.project_root / "assets"
        
        self._model_registry: dict[str, str] = {
            "agent_default": "models/misc/rgbCube",
            "player_default": "models/misc/rgbCube",
            "enemy_default": "models/misc/rgbCube",
            "interactable_default": "models/misc/rgbCube",
            "player9": "assets/models/characters/player9.glb",
        }
        self._actor_manifest_registry: dict[str, str] = {}
        self._warned_missing_models: set[str] = set()

    def _to_panda_filename(self, path: Path) -> str:
        return Filename.from_os_specific(str(path)).get_fullpath()


    def _to_panda_path(self, relative_or_absolute: str) -> str:
        path = Path(relative_or_absolute)
        if not path.is_absolute():
            path = self.project_root / path
        return Filename.from_os_specific(str(path)).get_fullpath()

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


    def _resolve_project_asset_path(self, model_path: str) -> str:
        # Built-in Panda assets should still load by Panda path.
        if model_path.startswith("models/"):
            return model_path

        path = Path(model_path)

        # If caller passed project-relative path like "assets/models/characters/player4.glb"
        if not path.is_absolute():
            path = self.project_root / path

        return self._to_panda_filename(path)

    def _load_model_path(self, model_path: str, parent: NodePath) -> NodePath:
        resolved_path = self._resolve_project_asset_path(model_path)
        model = self.base.loadModel(resolved_path)
        if model.isEmpty():
            raise RuntimeError(f"Loaded empty model for path: {resolved_path}")
        return model

    def load_model(self, requested_name: str | None, parent: NodePath) -> NodePath:
        resolved_name = self.resolve_model_name(requested_name)

        if resolved_name in self._actor_manifest_registry:
            try:
                actor = self.load_actor_from_manifest(self._actor_manifest_registry[resolved_name])
                return actor
            except Exception as exc:
                print(
                    f"[AssetLoader] Failed to load actor manifest for '{resolved_name}': {exc}. "
                    "Falling back to normal model load."
                )

        model_path = self._model_registry.get(resolved_name, "models/misc/rgbCube")

        try:
            return self._load_model_path(model_path, parent)
        except Exception as exc:
            if model_path != "models/misc/rgbCube":
                print(
                    f"[AssetLoader] Failed to load '{model_path}' for '{resolved_name}': {exc}. "
                    "Using rgbCube fallback."
                )
            return self._load_model_path("models/misc/rgbCube", parent)



    def _load_json(self, relative_path: str) -> dict:
        path = self.project_root / relative_path
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    def create_instance(self, requested_name: str | None, parent: NodePath) -> NodePath:
        model = self.load_model(requested_name, parent)
        if model.isEmpty():
            print(f"[Render] model for {requested_name} is empty")
            return model
    
        model.reparentTo(parent)
        print(f"[Render] requested={requested_name} node={model}")
        print(f"[Render] children={model.getNumChildren()}")
        print(f"[Render] tight bounds={model.getTightBounds()}")
        return model
    
    def load_actor_from_manifest(self, manifest_path: str) -> NodePath:
        manifest = self._load_json(manifest_path)

        model_path = self._to_panda_path(manifest["model"])

        animations = {}
        for anim_name, anim_rel_path in manifest.get("animations", {}).items():
            animations[anim_name] = self._to_panda_path(anim_rel_path)

        actor = Actor(model_path, animations if animations else None)

        scale = float(manifest.get("scale", 1.0))
        actor.setScale(scale)

        pos = manifest.get("position_offset", [0.0, 0.0, 0.0])
        actor.setPos(float(pos[0]), float(pos[1]), float(pos[2]))

        hpr = manifest.get("hpr", [0.0, 0.0, 0.0])
        actor.setHpr(float(hpr[0]), float(hpr[1]), float(hpr[2]))

        if manifest.get("two_sided", False):
            actor.setTwoSided(True)

        if manifest.get("use_shader_auto", False):
            actor.setShaderAuto()

        return actor
from __future__ import annotations

from panda3d.core import CardMaker, NodePath

from sim.components.renderable import Renderable
from sim.components.transform import Transform


class SimToRenderAdapter:
    def __init__(self, world, render: NodePath, asset_loader) -> None:
        self.world = world
        self.render = render
        self.asset_loader = asset_loader
        self.root_np: NodePath | None = None
        self.entity_nodes: dict[int, NodePath] = {}

    def rebuild(self) -> None:
        if self.root_np is not None:
            for node in self.entity_nodes.values():
                self._cleanup_node(node)
            self.root_np.removeNode()
            self.root_np = None
            self.entity_nodes.clear()

        self.root_np = self.render.attachNewNode("world_root")
        self._build_ground()
        self._build_entities()

    def _cleanup_node(self, node: NodePath) -> None:
        actor = node.getPythonTag("asset_actor")
        if actor is not None:
            try:
                actor.cleanup()
            except Exception:
                pass
        node.removeNode()

    def _build_ground(self) -> None:
        assert self.root_np is not None
        cm = CardMaker("ground")
        cm.setFrame(0, self.world.world_size, 0, self.world.world_size)
        ground = self.root_np.attachNewNode(cm.generate())
        ground.setP(-90)
        ground.setPos(0, 0, 0)
        ground.setColor(0.15, 0.18, 0.15, 1.0)

    def _build_entities(self) -> None:
        assert self.root_np is not None
        ecs = self.world.ecs

        for entity_id in ecs.query.entities_with(Transform, Renderable):
            transform = ecs.components.get_required(entity_id, Transform)
            renderable = ecs.components.get_required(entity_id, Renderable)

            node = self.asset_loader.create_instance(renderable.model_name, self.root_np)
            if node.isEmpty():
                continue

            if renderable.model_name == "player4":
                node.setScale(5.0)
                node.setZ(2.0)
                node.setHpr(180, 0, 0)
                node.setTwoSided(True)
                node.setColor(1, 0, 0, 1)
                node.setTextureOff(1)
                node.setMaterialOff(1)
                node.setShaderOff(1)
                node.showBounds()

            if bool(node.getPythonTag("asset_allow_tint")):
                node.setColor(*renderable.color)
            else:
                node.clearColor()

            if renderable.model_name == "player4":
                node.setPos(transform.x, transform.y, transform.z + 2.0)
            else:
                node.setPos(transform.x, transform.y, transform.z)
            self.entity_nodes[entity_id] = node

    def sync(self) -> None:
        ecs = self.world.ecs

        for entity_id, node in list(self.entity_nodes.items()):
            transform = ecs.components.get(entity_id, Transform)
            if transform is None:
                self._cleanup_node(node)
                del self.entity_nodes[entity_id]
                continue

            node.setPos(transform.x, transform.y, transform.z)
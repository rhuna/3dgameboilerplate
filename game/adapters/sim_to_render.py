from __future__ import annotations
from xml.parsers.expat import model

from mypyc import transform
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
            self.root_np.removeNode()
            self.root_np = None
            self.entity_nodes.clear()

        self.root_np = self.render.attachNewNode("world_root")
        self._build_ground()
        self._build_entities()

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

            model = self.asset_loader.create_instance(renderable.model_name, self.root_np)
            if model is None:
                continue

            model.setScale(1.0)
            model.setColor(*renderable.color)
            model.setPos(transform.x, transform.y, transform.z + 0.5)
            self.entity_nodes[entity_id] = model

    def sync(self) -> None:
        ecs = self.world.ecs

        for entity_id, node in list(self.entity_nodes.items()):
            transform = ecs.components.get(entity_id, Transform)
            if transform is None:
                node.removeNode()
                del self.entity_nodes[entity_id]
                continue

            node.setPos(transform.x, transform.y, transform.z)
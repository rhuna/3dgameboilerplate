from __future__ import annotations

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import ClockObject, WindowProperties
from game.adapters.sim_to_render import SimToRenderAdapter
from app.settings import AppSettings
from engine.asset_loader import AssetLoader
from engine.camera import CameraController
from engine.debug_overlay import DebugOverlay
from engine.input import InputState
from sim.world import World
import time
import simplepbr
from sim.components.agent_tag import AgentTag
from sim.components.health import Health
from sim.components.mana import Mana
from sim.components.transform import Transform
from game.scenes.simulation_scene import SimulationScene
from sim.commands import SetWeatherCommand
from game.adapters.input_to_commands import InputToCommandsAdapter




class SimulationGameApp(ShowBase):
    def __init__(
                    self, 
                    settings: AppSettings, 
                    scenario=None, 
                    content=None, 
                    event_bus=None, 
                    services=None
            )  -> None:
            self.settings = settings
            self.world = World.create(
                settings=settings,
                content=content,
                event_bus=event_bus,
                services=services,
                scenario=scenario,
            )
            self.scenario = scenario
            self.content = content
            self.event_bus = event_bus
            self.services = services

            
            super().__init__()
            try:
                simplepbr.init()
            except Exception as exc:
                print(f"[Render] simplepbr not enabled: {exc}")
            self.asset_loader = AssetLoader(self.loader)

            if self.services is not None:
                self.services.set("app", self)
                self.services.set("world", self.world)
                self.services.set("asset_loader", self.asset_loader)
        
            
            self.input_state = InputState()
            self.command_adapter = InputToCommandsAdapter(self.input_state, self.world)
            self.camera_controller = CameraController(self, settings.camera, self.input_state)
            self.debug_overlay = DebugOverlay(self)
            self.fixed_dt = 1.0 / self.settings.simulation.sim_hz
            self.accumulator = 0.0

            self._configure_window()
            self._configure_scene()
            self.sim_renderer = SimToRenderAdapter(
                world=self.world,
                render=self.render,
                asset_loader=self.asset_loader,
            )
            self._configure_input()
            self._configure_timing()
            self._spawn_visuals()

            self.taskMgr.add(self._update, "main_update")
            self._apply_scenario_camera()
            self.last_frame_dt = 0.0
            self.last_sim_step_count = 0
            self.last_sim_step_time_ms = 0.0
            self.selected_agent_id: int | None = None

            
            
    def _get_selected_agent_debug_text(self) -> str:
        entity_id = self.selected_agent_id
        if entity_id is None:
            return "Selected: None"
    
        if entity_id not in self.world.ecs.entities.all_entities():
            return "Selected: Missing"
    
        tag = self.world.ecs.components.get(entity_id, AgentTag)
        health = self.world.ecs.components.get(entity_id, Health)
        mana = self.world.ecs.components.get(entity_id, Mana)
        transform = self.world.ecs.components.get(entity_id, Transform)
        spellbook = self.world.ecs.components.get(entity_id, Spellbook)
    
        role = tag.role if tag is not None else "unknown"
        hp = health.current if health is not None else 0.0
        mp = mana.current if mana is not None else 0.0
        x = transform.x if transform is not None else 0.0
        y = transform.y if transform is not None else 0.0
        spell = spellbook.selected_spell if spellbook is not None else "none"
    
        return (
            f"Selected: id={entity_id} "
            f"role={role} "
            f"hp={hp:.1f} "
            f"mana={mp:.1f} "
            f"spell={spell} "
            f"pos=({x:.1f}, {y:.1f})"
        )



    def _apply_scenario_camera(self) -> None:
        if self.scenario is None:
            return

        camera_data = getattr(self.scenario, "camera", None)
        if not camera_data:
            return
    
        x = float(camera_data.get("x", 20.0))
        y = float(camera_data.get("y", -30.0))
        z = float(camera_data.get("z", 25.0))
    
        look_at_x = float(camera_data.get("look_at_x", 20.0))
        look_at_y = float(camera_data.get("look_at_y", 20.0))
        look_at_z = float(camera_data.get("look_at_z", 0.0))
    
        self.camera.setPos(x, y, z)
        self.camera.lookAt(look_at_x, look_at_y, look_at_z)
    
    def load(self) -> None:
        self.scene = SimulationScene(self)
        self.scene.load()
        self.scene.activate()

    def _configure_window(self) -> None:
        props = WindowProperties()
        props.setTitle(self.settings.window.title)
        props.setSize(self.settings.window.width, self.settings.window.height)
        props.setFullscreen(self.settings.window.fullscreen)
        self.win.requestProperties(props)

    def _configure_scene(self) -> None:
        self.scene = SimulationScene(self)
        self.scene.load()
        self.scene.activate()

    def _configure_input(self) -> None:
        key_pairs = [
            "w", "a", "s", "d", "q", "e", "shift",
            "mouse1", "mouse3",
            "f1", "r", "space", "t",
            "wheel_up", "wheel_down",
            "1", "2", "3", "4", "5", "6", "7", "8", "9",
            "f5", "f9",
        ]

        for key in key_pairs:
            self.accept(key, self._on_press, [key])
            self.accept(f"{key}-up", self._on_release, [key])

    def _configure_timing(self) -> None:
        clock = ClockObject.getGlobalClock()
        clock.setMode(ClockObject.MLimited)
        clock.setFrameRate(120)

    def _spawn_visuals(self) -> None:
        self.sim_renderer.rebuild()
        


    def _on_press(self, key: str) -> None:
        if key == "f1":
            self.debug_overlay.toggle()
            return
        if key == "r":
            self.world.reset()
            return
        if key == "space":
            self.input_state.paused = not self.input_state.paused
            return
        if key == "t":
            self.input_state.single_step_requested = True
            return
        if key == "mouse3":
            self.input_state.mouse_held = True
            return
        if key == "wheel_up":
            self.camera_controller.zoom(-1.0)
            return
        if key == "wheel_down":
            self.camera_controller.zoom(+1.0)
            return
        if key == "f5":
            self.world.save("data/saves/quicksave.json")
            return
        if key == "f9":
            self.world.load("data/saves/quicksave.json")
            self.sim_renderer.rebuild()
            return
        if key == "c":
            self.world.issue_command(SetWeatherCommand(weather="clear"))
            return
        if key == "f":
            self.world.issue_command(SetWeatherCommand(weather="rain"))
            return

        self.input_state.press(key)

    def _on_release(self, key: str) -> None:
        if key == "mouse3":
            self.input_state.mouse_held = False
            return
        self.input_state.release(key)

    def _update(self, task: Task) -> Task:
        dt = min(ClockObject.getGlobalClock().getDt(), 0.25)
        self.accumulator += dt

        # Collect player input commands once per frame.
        commands = self.command_adapter.get_commands()
        for command in commands:
            self.world.issue_command(command)

        sim_start = time.perf_counter()
        steps_executed = 0

        # Respect pause / single-step controls.
        if self.input_state.paused:
            if self.input_state.single_step_requested:
                self.world.tick()
                self.input_state.single_step_requested = False
                steps_executed = 1
                self.accumulator = 0.0
        else:
            scaled_dt = dt * self.input_state.sim_speed
            self.accumulator = min(self.accumulator + (scaled_dt - dt), self.fixed_dt * 8.0)

            while self.accumulator >= self.fixed_dt:
                self.world.tick()
                self.accumulator -= self.fixed_dt
                steps_executed += 1

        self.last_frame_dt = dt
        self.last_sim_step_count = steps_executed
        self.last_sim_step_time_ms = (time.perf_counter() - sim_start) * 1000.0

        # Camera should update after simulation so it follows the latest world state.
        self.camera_controller.update(dt)

        # Push ECS/sim state to render nodes.
        self.sim_renderer.sync()

        # Refresh debug text without relying on a missing overlay.update() API.
        self._refresh_debug()

        return task.cont

    def _refresh_debug(self) -> None:
        fps = 0.0 if self.last_frame_dt <= 0.0 else 1.0 / self.last_frame_dt
        metrics = self.world.get_metrics()

        cam_x, cam_y, cam_z = self.camera.getPos()

        selected_text = self._get_selected_agent_debug_text()

        resource_summary = ", ".join(
            f"{k}={v:.0f}" for k, v in self.world.state.resources.items()
        )
        if not resource_summary:
            resource_summary = "None"

        debug_lines = [
            f"FPS: {fps:.1f}",
            f"Frame DT: {self.last_frame_dt * 1000.0:.2f} ms",
            f"Sim Time: {self.world.clock.sim_time:.2f}",
            f"Step Count: {self.world.clock.step_count}",
            f"Sim Steps This Frame: {self.last_sim_step_count}",
            f"Sim Tick Time: {self.last_sim_step_time_ms:.3f} ms",
            f"Avg Temp: {metrics.get('avg_temperature', 0.0):.3f}",
            f"Paused: {self.input_state.paused}",
            f"Entity Count: {len(self.world.agent_ids)}",
            f"Sim Speed: {self.input_state.sim_speed:.1f}x",
            f"Seed: {self.settings.simulation.random_seed}",
            f"Weather: {self.settings.simulation.weather}",
            f"Camera: ({cam_x:.2f}, {cam_y:.2f}, {cam_z:.2f})",
            selected_text,
            f"Resources: {resource_summary}",
        ]

        self.debug_overlay.set_text("\n".join(debug_lines))

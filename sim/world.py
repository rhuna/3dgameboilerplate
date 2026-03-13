from __future__ import annotations

import math
import random
from dataclasses import asdict, is_dataclass
from pathlib import Path
from game.gameplay.commands import MovePlayerCommand
from game.definitions.registry import ContentRegistry
from sim import ecs
from sim.analysis.exporters import export_metrics_csv, export_metrics_json
from sim.clock import SimulationClock
from sim.components import movement
from sim.components.agent_tag import AgentTag
from sim.components.ai_state import AIState
from sim.components.combat_stats import CombatStats
from sim.components.cooldowns import Cooldowns
from sim.components.enemy_tag import EnemyTag
from sim.components.faction import Faction
from sim.components.facing import Facing
from sim.components.health import Health
from sim.components.mana import Mana
from sim.components.move_intent import MoveIntent
from sim.components.movement import Movement
from sim.components.player_tag import PlayerTag
from sim.components.renderable import Renderable
from sim.components.spellbook import Spellbook
from sim.components.temperature_emitter import TemperatureEmitter
from sim.components.transform import Transform
from sim.components.velocity import Velocity
from sim.ecs.world_ecs import ECSWorld
from sim.replay.io import save_replay
from sim.replay.recorder import ReplayRecorder
from sim.save_load import deserialize_ecs, deserialize_world_state, load_snapshot, save_snapshot, serialize_ecs, serialize_world_state
from sim.scheduler import SystemScheduler
from sim.state import WorldState
from sim.system_installers import install_core_systems, install_game_systems
from sim.analysis.recorder import MetricsRecorder
from tests.test_ecs_stability import Position


class World:
    def __init__(self, settings, scenario=None, content=None, event_bus=None, services=None) -> None:
        self.settings = settings
        self.scenario = scenario
        self.scenario_name = getattr(scenario, "name", None)
        self.content = content or ContentRegistry.load_defaults()
        self.event_bus = event_bus
        self.services = services
        self.world_size = settings.simulation.world_size
        self.fixed_dt = 1.0 / settings.simulation.sim_hz
        self.rng = random.Random(settings.simulation.random_seed)
        self.metrics = MetricsRecorder()
        self.replay = self._create_replay_recorder()
        self.ecs = ECSWorld()
        self.clock = SimulationClock(fixed_dt=self.fixed_dt)
        self.state = WorldState.create(size=self.world_size)
        self.scheduler = SystemScheduler()
        install_core_systems(self)
        install_game_systems(self)
        if self.services is not None:
            self.services.set("world", self)
        self.reset()

    @classmethod
    def create(cls, settings, *, scenario=None, content=None, services=None, event_bus=None) -> "World":
        return cls(settings=settings, scenario=scenario, content=content, services=services, event_bus=event_bus)

    def _create_replay_recorder(self) -> ReplayRecorder:
        return ReplayRecorder(
            sim_version="0.1.0",
            seed=self.settings.simulation.random_seed,
            world_size=self.world_size,
            sim_hz=self.settings.simulation.sim_hz,
            scenario_name=self.scenario_name,
            snapshot_interval=100,
        )

    @property
    def step_count(self) -> int:
        return self.clock.step_count

    @property
    def agent_ids(self) -> list[int]:
        return sorted(self.ecs.query.entities_with(AgentTag))

    @property
    def resources(self) -> dict[str, float]:
        return self.state.resources

    @property
    def temperatures(self):
        return self.state.temperature
    
    

    def reset(self) -> None:
        self.rng = random.Random(self.settings.simulation.random_seed)
        self.ecs = ECSWorld()
        self.clock = SimulationClock(fixed_dt=self.fixed_dt)
        self.state = WorldState.create(size=self.world_size)
        self.metrics.clear()
        self.replay = self._create_replay_recorder()

        self.environment_system.seed_temperature(
            self.state.temperature,
            base=self.settings.simulation.temperature_base,
            weather=self.settings.simulation.weather,
        )

        self.state.resources = {
            key: value["starting_amount"]
            for key, value in self.content.resources.items()
        }

        if self.scenario is not None and getattr(self.scenario, "game_mode", "sandbox") == "adventure":
            self.spawn_player(x=20.0, y=20.0)
            self.spawn_enemy(x=26.0, y=20.0)
            self.spawn_enemy(x=30.0, y=24.0)
        else:
            total_agents = int(self.settings.simulation.initial_agents)
            fire_wizards = total_agents // 2
            villagers = total_agents - fire_wizards

            self._spawn_archetype("fire_wizard", fire_wizards)
            self._spawn_archetype("villager", villagers)

        self.metrics_system.update(self)

        reset_payload = {
            "seed": self.settings.simulation.random_seed,
            "world_size": self.world_size,
            "scenario_name": self.scenario_name,
        }

        self.replay.record_event(
            self.step_count,
            "simulation_reset",
            reset_payload,
        )
        self.replay.record_snapshot(self.step_count, self.to_dict())

        if self.event_bus is not None:
            self.event_bus.emit("simulation_reset", reset_payload)
    def _spawn_adventure_defaults(self) -> None:
        self.event_bus.emit("message", {"text": "Welcome to the adventure! Prepare to face the Ash Crawlers lurking in the fiery depths."})
        self.spawn_player(archetype="player_fire_wizard", x=self.world_size * 0.5, y=self.world_size * 0.5)
        self.spawn_enemy(archetype="ash_crawler", x=self.world_size * 0.5 + 6.0, y=self.world_size * 0.5 + 2.0)
        self.spawn_enemy(archetype="ash_crawler", x=self.world_size * 0.5 - 7.0, y=self.world_size * 0.5 + 4.0)

    def _spawn_wanderers(self, archetype: str, count: int) -> None:
        for _ in range(count):
            entity_id = self.ecs.create_entity()
            data = self.content.get_agent(archetype)
            x = self.rng.uniform(0, self.world_size - 1)
            y = self.rng.uniform(0, self.world_size - 1)
            target_x = self.rng.uniform(0, self.world_size - 1)
            target_y = self.rng.uniform(0, self.world_size - 1)
            self.ecs.components.add(entity_id, Transform(x=x, y=y, z=0.25))
            self.ecs.components.add(entity_id, Movement(speed=float(data.get("speed", 3.0)), target_x=target_x, target_y=target_y))
            self.ecs.components.add(entity_id, Health(current=float(data.get("health", 100.0)), maximum=float(data.get("health", 100.0))))
            self.ecs.components.add(entity_id, Mana(current=float(data.get("mana", 0.0)), maximum=float(data.get("mana", 0.0))))
            self.ecs.components.add(entity_id, Faction(name=str(data.get("faction", "neutral"))))
            self.ecs.components.add(entity_id, AgentTag(archetype=archetype, role=str(data.get("role", "npc")), state=str(data.get("state", "idle"))))
            self.ecs.components.add(
                entity_id,
                Renderable(
                    model_name=archetype["model"],
                    color=archetype["color"]
                ),
            )
            self.ecs.components.add(entity_id, TemperatureEmitter(amount=0.01))

    def _spawn_actor(self, *, archetype: str, x: float, y: float, role_override: str | None = None, is_player: bool = False, is_enemy: bool = False) -> int:
        entity_id = self.ecs.create_entity()
        data = self.content.get_agent(archetype)
        role = role_override or str(data.get("role", "npc"))
        health_value = float(data.get("health", 100.0))
        mana_value = float(data.get("mana", 0.0))
        speed_value = float(data.get("speed", 3.0))
        self.ecs.components.add(entity_id, Transform(x=x, y=y, z=0.25))
        self.ecs.components.add(entity_id, Velocity())
        self.ecs.components.add(entity_id, MoveIntent())
        self.ecs.components.add(entity_id, Facing())
        self.ecs.components.add(entity_id, Health(current=health_value, maximum=health_value))
        self.ecs.components.add(entity_id, Mana(current=mana_value, maximum=mana_value))
        self.ecs.components.add(entity_id, Faction(name=str(data.get("faction", "neutral"))))
        tag = AgentTag(archetype=archetype, role=role, state=str(data.get("state", "idle")))
        tag.move_speed = speed_value
        self.ecs.components.add(entity_id, tag)
        self.ecs.components.add(
            entity_id,
            Renderable(
                model_name=archetype["model"],
                color=archetype["color"]
            )
        )
        self.ecs.components.add(entity_id, TemperatureEmitter(amount=0.01))
        self.ecs.components.add(entity_id, Cooldowns())
        self.ecs.components.add(entity_id, CombatStats())
        if is_player:
            self.ecs.components.add(entity_id, PlayerTag())
            self.ecs.components.add(entity_id, Spellbook(slots=["fireball", "flame_burst"], selected_index=0))
        if is_enemy:
            self.ecs.components.add(entity_id, EnemyTag())
            self.ecs.components.add(entity_id, AIState())
        return entity_id

    def spawn_player(self, *, x: float, y: float, archetype: str = "fire_wizard") -> int:
        entity_id = self.ecs.create_entity()
        data = self.content.get_agent(archetype)
        self.ecs.components.add(entity_id, Transform(x=x, y=y, z=0.25))
        self.ecs.components.add(
            entity_id,
            Movement(
                speed=float(data.get("speed", 5.0)),
                target_x=x,
                target_y=y,
            ),
        )
        self.ecs.components.add(
            entity_id,
            Health(
                current=float(data.get("health", 100.0)),
                maximum=float(data.get("health", 100.0)),
            ),
        )
        self.ecs.components.add(
            entity_id,
            Mana(
                current=float(data.get("mana", 120.0)),
                maximum=float(data.get("mana", 120.0)),
            ),
        )
        self.ecs.components.add(entity_id, Faction(name=str(data.get("faction", "fire"))))
        self.ecs.components.add(
            entity_id,
            AgentTag(
                archetype=archetype,
                role="player",
                state=str(data.get("state", "idle")),
            ),
        )
        self.ecs.components.add(entity_id, PlayerTag())
        self.ecs.components.add(
            entity_id,
            Renderable(
                model_name=str(data.get("model", "fire_wizard_model")),
                color=tuple(data.get("color", (1.0, 0.45, 0.1, 1.0))),
            ),
        )
        self.ecs.components.add(entity_id, TemperatureEmitter(amount=0.02))
        spawn_payload = {
            "entity_id": entity_id,
            "archetype": archetype,
            "role": "player",
        }
        self.replay.record_event(self.step_count, "entity_spawned", spawn_payload)
        if self.event_bus is not None:
            self.event_bus.emit("entity_spawned", spawn_payload)
        return entity_id

    def _spawn_archetype(self, archetype_name: str, count: int) -> None:
        for _ in range(count):
            x = self.rng.uniform(0.0, float(self.world_size - 1))
            y = self.rng.uniform(0.0, float(self.world_size - 1))
            self.spawn_agent(archetype_name, x=x, y=y)


    def spawn_agent(self, archetype_name: str, x: float, y: float) -> int:
        entity_id = self.ecs.create_entity()
        data = self.content.get_agent(archetype_name)

        target_x = self.rng.uniform(0, self.world_size - 1)
        target_y = self.rng.uniform(0, self.world_size - 1)

        self.ecs.components.add(entity_id, Transform(x=x, y=y, z=0.25))
        self.ecs.components.add(
            entity_id,
            Movement(
                speed=float(data.get("speed", 3.0)),
                target_x=target_x,
                target_y=target_y,
            ),
        )
        self.ecs.components.add(
            entity_id,
            Health(
                current=float(data.get("health", 100.0)),
                maximum=float(data.get("health", 100.0)),
            ),
        )
        self.ecs.components.add(
            entity_id,
            Mana(
                current=float(data.get("mana", 0.0)),
                maximum=float(data.get("mana", 0.0)),
            ),
        )
        self.ecs.components.add(
            entity_id,
            Faction(name=str(data.get("faction", "neutral"))),
        )
        self.ecs.components.add(
            entity_id,
            AgentTag(
                archetype=archetype_name,
                role=str(data.get("role", "npc")),
                state=str(data.get("state", "idle")),
            ),
        )
        self.ecs.components.add(
            entity_id,
            Renderable(
                model_name=str(data.get("model", "agent_default")),
                color=tuple(data.get("color", (1.0, 1.0, 1.0, 1.0))),
            ),
        )
        self.ecs.components.add(entity_id, TemperatureEmitter(amount=0.01))

        spawn_payload = {
            "entity_id": entity_id,
            "archetype": archetype_name,
            "role": str(data.get("role", "npc")),
        }

        self.replay.record_event(self.step_count, "entity_spawned", spawn_payload)

        if self.event_bus is not None:
            self.event_bus.emit("entity_spawned", spawn_payload)

        return entity_id

    def spawn_enemy(self, *, x: float, y: float, archetype: str = "ash_crawler") -> int:
        entity_id = self.ecs.create_entity()
        data = self.content.get_agent(archetype)

        self.ecs.components.add(entity_id, Transform(x=x, y=y, z=0.25))
        self.ecs.components.add(
            entity_id,
            Movement(
                speed=float(data.get("speed", 4.0)),
                target_x=x,
                target_y=y,
            ),
        )
        self.ecs.components.add(
            entity_id,
            Health(
                current=float(data.get("health", 50.0)),
                maximum=float(data.get("health", 50.0)),
            ),
        )
        self.ecs.components.add(
            entity_id,
            Mana(
                current=float(data.get("mana", 0.0)),
                maximum=float(data.get("mana", 0.0)),
            ),
        )
        self.ecs.components.add(entity_id, Faction(name=str(data.get("faction", "ash"))))
        self.ecs.components.add(
            entity_id,
            AgentTag(
                archetype=archetype,
                role="enemy",
                state=str(data.get("state", "idle")),
            ),
        )
        self.ecs.components.add(entity_id, EnemyTag())
        self.ecs.components.add(
            entity_id,
            Renderable(
                model_name=str(data.get("model", "ash_crawler_model")),
                color=tuple(data.get("color", (0.35, 0.35, 0.35, 1.0))),
            ),
        )
        self.ecs.components.add(entity_id, TemperatureEmitter(amount=0.01))

        spawn_payload = {
            "entity_id": entity_id,
            "archetype": archetype,
            "role": "enemy",
        }

        self.replay.record_event(self.step_count, "entity_spawned", spawn_payload)

        if self.event_bus is not None:
            self.event_bus.emit("entity_spawned", spawn_payload)

        return entity_id

    def find_player_id(self) -> int | None:
        player_ids = sorted(self.ecs.query.entities_with(PlayerTag))
        if not player_ids:
            return None
        return player_ids[0]

    def get_entity_position(self, entity_id: int) -> tuple[float, float, float]:
        transform = self.ecs.components.get_required(entity_id, Transform)
        return (transform.x, transform.y, transform.z)

    def get_entity_speed(self, entity_id: int) -> float:
        tag = self.ecs.components.get(entity_id, AgentTag)
        if tag is None:
            return 0.0
        return float(getattr(tag, "move_speed", 0.0))

    def get_selected_spell(self, entity_id: int) -> str:
        spellbook = self.ecs.components.get(entity_id, Spellbook)
        if spellbook is None:
            return "fireball"
        return spellbook.selected_spell

    def step_real_time(self, dt: float) -> int:
        steps = self.clock.add_real_time(dt)
        for _ in range(steps):
            self.tick()
        return steps

    def tick(self) -> None:
        timer = self.metrics.make_step_timer()
        try:
            self.scheduler.run(self)
            self._tick_cooldowns()
            self.clock.advance_one_step()
        except Exception as exc:
            self.metrics.record_error()
            self.replay.record_event(self.step_count, "simulation_error", {"message": str(exc)})
            raise
        finally:
            self.metrics.record_step(self, timer.elapsed_ms())
        self.replay.maybe_record_snapshot(self)
        if self.clock.step_count % 100 == 0:
            export_metrics_csv(self.metrics, "output/metrics.csv")
            export_metrics_json(self.metrics, "output/metrics.json")

    def _tick_cooldowns(self) -> None:
        for entity_id in self.ecs.query.entities_with(Cooldowns):
            cooldowns = self.ecs.components.get_required(entity_id, Cooldowns)
            for key, value in list(cooldowns.timers.items()):
                cooldowns.timers[key] = max(0.0, value - self.fixed_dt)

    def get_metrics(self) -> dict[str, float]:
        if self.event_bus is not None:
            self.event_bus.emit("metrics_updated", {"metrics": self.state.metrics})
        return dict(self.state.metrics)

    def record_command(self, command_type: str, payload: dict) -> None:
        self.replay.record_command(step=self.step_count, command_type=command_type, payload=payload)

    def save(self, path: str | Path) -> None:
        payload = self.to_dict()
        save_snapshot(path, payload)
        save_payload = {"path": str(path), "scenario_name": self.scenario_name}
        self.replay.record_event(self.step_count, "world_saved", save_payload)
        if self.event_bus is not None:
            self.event_bus.emit("world_saved", save_payload)

    def load(self, path: str | Path) -> None:
        payload = load_snapshot(path)
        _version = payload.get("snapshot_version", 1)
        self.scenario_name = payload.get("scenario_name")
        self.world_size = int(payload["world_size"])
        self.fixed_dt = float(payload["fixed_dt"])
        self.rng = random.Random(int(payload["random_seed"]))
        self.clock = SimulationClock(fixed_dt=self.fixed_dt)
        self.clock.sim_time = float(payload.get("sim_time", 0.0))
        self.clock.step_count = int(payload.get("step_count", 0))
        self.clock.accumulator = float(payload.get("accumulator", 0.0))
        self.state = deserialize_world_state(WorldState, payload["state"])
        self.ecs = ECSWorld()
        deserialize_ecs(self.ecs, payload["ecs"])
        self.scheduler = SystemScheduler()
        install_core_systems(self)
        install_game_systems(self)
        if self.services is not None:
            self.services.set("world", self)
        load_payload = {"path": str(path), "scenario_name": self.scenario_name}
        self.replay.record_event(self.step_count, "world_loaded", load_payload)
        self.replay.record_snapshot(self.step_count, self.to_dict())
        if self.event_bus is not None:
            self.event_bus.emit("world_loaded", load_payload)

    def save_replay(self, path: str | Path) -> None:
        save_replay(path, self.replay.data)
        if self.event_bus is not None:
            self.event_bus.emit("replay_saved", {"path": str(path), "step_count": self.step_count})

    def to_dict(self) -> dict:
        return {
            "snapshot_version": 1,
            "scenario_name": self.scenario_name,
            "world_size": self.world_size,
            "fixed_dt": self.fixed_dt,
            "random_seed": self.settings.simulation.random_seed,
            "sim_time": self.clock.sim_time,
            "step_count": self.clock.step_count,
            "accumulator": self.clock.accumulator,
            "state": serialize_world_state(self.state),
            "ecs": serialize_ecs(self.ecs),
        }

    def issue_command(self, command: object) -> None:
        if is_dataclass(command):
            payload = asdict(command)
        elif hasattr(command, "__dict__"):
            payload = dict(command.__dict__)
        else:
            raise TypeError(f"Commands must be dataclasses or expose __dict__; got {type(command).__name__}")
        self.record_command(command_type=command.__class__.__name__, payload=payload)
        self._apply_command(command)


    @property
    def entities(self):
        entity_manager = self.ecs.entities
    
        if hasattr(entity_manager, "_alive"):
            return entity_manager._alive
    
        if hasattr(entity_manager, "alive"):
            return entity_manager.alive
    
        if hasattr(entity_manager, "_entities"):
            return entity_manager._entities
    
        if hasattr(entity_manager, "entities"):
            return entity_manager.entities
    
        raise AttributeError("Could not find iterable entity set on EntityManager")


    def create_entity(self) -> int:
        return self.ecs.create_entity()


    def destroy_entity(self, entity_id: int) -> None:
        self.ecs.destroy_entity(entity_id)


    def add_component(self, entity_id: int, component: object) -> None:
        self.ecs.add_component(entity_id, component)


    def remove_component(self, entity_id: int, component_type: type) -> None:
        self.ecs.remove_component(entity_id, component_type)


    def get_component(self, entity_id: int, component_type: type):
        return self.ecs.get_component(entity_id, component_type)


    def has_component(self, entity_id: int, component_type: type) -> bool:
        return self.ecs.has_component(entity_id, component_type)


    def query(self, *component_types: type):
        return self.ecs.query_iter(*component_types)

    def _apply_command(self, command: object) -> None:
        if isinstance(command, MovePlayerCommand):
            player_id = self.find_player_id()
            if player_id is None:
                return
            transform = self.ecs.components.get(player_id, Transform)
            movement = self.ecs.components.get(player_id, Movement)
            if transform is None or movement is None:
                return
            length = math.hypot(command.move_x, command.move_y)
            if length <= 0.0:
                return

            dir_x = command.move_x / length
            dir_y = command.move_y / length
            target_distance = max(1.0, movement.speed * self.fixed_dt * 6.0)
            entity_radius = 0.5

            movement.target_x = max(
                entity_radius,
                min(self.world_size - entity_radius, transform.x + dir_x * target_distance),
            )
            movement.target_y = max(
                entity_radius,
                min(self.world_size - entity_radius, transform.y + dir_y * target_distance),
            )
            return

        command_name = command.__class__.__name__

        if command_name == "SetWeatherCommand":
            self.settings.simulation.weather = command.weather
            self.environment_system.seed_temperature(
                self.state.temperature,
                base=self.settings.simulation.temperature_base,
                weather=command.weather,
            )
            return

        if command_name == "SpawnEntityCommand":
            entity_id = self.ecs.create_entity()
            data = self.content.get_agent(command.archetype)

            self.ecs.components.add(entity_id, Transform(x=command.x, y=command.y, z=0.25))
            self.ecs.components.add(
                entity_id,
                Movement(
                    speed=float(data.get("speed", 3.0)),
                    target_x=command.x,
                    target_y=command.y,
                ),
            )
            self.ecs.components.add(
                entity_id,
                Health(
                    current=float(data.get("health", 100.0)),
                    maximum=float(data.get("health", 100.0)),
                ),
            )
            self.ecs.components.add(
                entity_id,
                Mana(
                    current=float(data.get("mana", 0.0)),
                    maximum=float(data.get("mana", 0.0)),
                ),
            )
            self.ecs.components.add(entity_id, Faction(name=str(data.get("faction", "neutral"))))
            self.ecs.components.add(
                entity_id,
                AgentTag(
                    archetype=command.archetype,
                    role=str(data.get("role", "npc")),
                    state=str(data.get("state", "idle")),
                ),
            )
            self.ecs.components.add(
                entity_id,
                Renderable(
                    model_name=str(data.get("model", "agent_default")),
                    color=tuple(data.get("color", (1.0, 1.0, 1.0, 1.0))),
                ),
            )
            self.ecs.components.add(entity_id, TemperatureEmitter(amount=0.01))

            spawn_payload = {
                "entity_id": entity_id,
                "archetype": command.archetype,
            }
            self.replay.record_event(self.step_count, "entity_spawned", spawn_payload)

            if self.event_bus is not None:
                self.event_bus.emit("entity_spawned", spawn_payload)

            return

        raise ValueError(f"Unsupported command type: {command_name}")

    def _cast_spell(self, caster_id: int, spell_id: str) -> None:
        spell = self.content.get_spell(spell_id)
        caster_transform = self.ecs.components.get(caster_id, Transform)
        caster_mana = self.ecs.components.get(caster_id, Mana)
        cooldowns = self.ecs.components.get(caster_id, Cooldowns)
        if caster_transform is None or caster_mana is None or cooldowns is None:
            return
        if cooldowns.timers.get(spell_id, 0.0) > 0.0:
            return
        mana_cost = float(spell.get("mana_cost", 0.0))
        if caster_mana.current < mana_cost:
            return
        range_limit = float(spell.get("range", 10.0))
        damage = float(spell.get("damage", 0.0))
        target_id = None
        best_distance = None
        for entity_id in self.ecs.query.entities_with(EnemyTag, Transform, Health):
            target_transform = self.ecs.components.get_required(entity_id, Transform)
            dx = target_transform.x - caster_transform.x
            dy = target_transform.y - caster_transform.y
            distance = math.hypot(dx, dy)
            if distance <= range_limit and (best_distance is None or distance < best_distance):
                best_distance = distance
                target_id = entity_id
        if target_id is None:
            return
        target_health = self.ecs.components.get_required(target_id, Health)
        caster_mana.current -= mana_cost
        cooldowns.timers[spell_id] = float(spell.get("cooldown", 0.5))
        target_health.current -= damage

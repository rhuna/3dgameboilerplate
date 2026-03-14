from sim.systems.combat_system import CombatSystem
from sim.systems.death_system import DeathSystem
from sim.systems.environment_system import EnvironmentSystem
from sim.systems.metrics_system import MetricsSystem
from sim.systems.movement_system import MovementSystem
from game.gameplay.enemy_ai_system import EnemyAISystem
from game.gameplay.player_controller_system import PlayerControllerSystem


def install_core_systems(world) -> None:
    world.environment_system = EnvironmentSystem(world.world_size)
    world.enemy_ai_system = EnemyAISystem()
    world.player_controller_system = PlayerControllerSystem()
    world.movement_system = MovementSystem()
    world.combat_system = CombatSystem()
    world.death_system = DeathSystem()
    world.metrics_system = MetricsSystem()

    world.scheduler.clear()
    world.scheduler.add(world.environment_system)
    world.scheduler.add(world.enemy_ai_system)
    world.scheduler.add(world.movement_system)
    world.scheduler.add(world.combat_system)
    world.scheduler.add(world.death_system)
    world.scheduler.add(world.metrics_system)


def install_game_systems(world) -> None:
    pass
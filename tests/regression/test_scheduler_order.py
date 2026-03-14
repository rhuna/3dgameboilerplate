





def test_scheduler_order_is_stable(world):
    actual = world.scheduler.names()
    print(actual)
    assert actual == [
        "environment_system",
        "enemy_ai_system",
        "player_movement_system",
        "MovementSystem",
        "combat_system",
        "death_system",
        "metrics_system",
    ]
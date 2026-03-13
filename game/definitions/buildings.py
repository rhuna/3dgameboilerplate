

''' 
towers, shrines, labs, houses, shops, etc. 
that can be built by the player or NPCs. 
They can have various functions such as producing resources, 
providing buffs, or serving as defensive structures.

'''


BUILDING_DEFINITIONS = {
    "watch_tower": {
        "health": 150.0,
        "cost": {"wood": 20.0},
        "size": 2,
        "heat_output": 0.0,
    },
    "mana_shrine": {
        "health": 120.0,
        "cost": {"wood": 10.0, "ember_dust": 5.0},
        "size": 2,
        "heat_output": 0.1,
    },
    "fire_lab": {
        "health": 100.0,
        "cost": {"wood": 15.0, "mana": 25.0},
        "size": 3,
        "heat_output": 0.25,
    },
}
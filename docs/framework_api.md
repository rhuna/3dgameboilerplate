# Framework API

These APIs are considered stable for building future games on the framework.

## Stable World API

- World.create(...)
- world.reset()
- world.tick()
- world.step_real_time(dt)
- world.get_metrics()
- world.issue_command(command)
- world.save(path)
- world.load(path)
- world.save_replay(path)

## Stable Scene Lifecycle

- load()
- activate()
- update(dt)
- deactivate()
- unload()

## Stable System Registration

- install_core_systems(world)
- install_game_systems(world)

## Stable Content Loading

- ContentRegistry.load_defaults()

## Internal / Not Frozen

- ECS storage internals
- scheduler internals
- exact save JSON schema
- exact replay storage strategy
- render node implementation details

## Adapter Rules

Adapters translate between layers.

Examples:

- simulation to rendering
- input to commands
- world state to debug UI

Adapters may:

- read simulation state
- transform data for rendering or UI
- issue commands through the World command API

Adapters may not:

- implement gameplay rules
- directly mutate simulation state except through stable public APIs
- bypass command issuance for external actions

## Stable Content API

Game content should be provided through ContentRegistry.

Stable entry point:

- ContentRegistry.load_defaults()

Future games may provide additional content-loading helpers, but should preserve a single clear entry point.

## Stable Bootstrap Pattern

Framework startup should follow this order:

1. Load settings
2. Load content
3. Create world
4. Create scene/application objects
5. Run the app loop


## Stable Read-Only World Inspection

- world.step_count
- world.agent_ids
- world.get_metrics()

These are stable read-only inspection points for UI, debug, and tooling.

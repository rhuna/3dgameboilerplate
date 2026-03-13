# Save Format

FireWizard3D uses JSON-based snapshots for save files.

Snapshots capture the entire simulation state.

---

# Snapshot Structure

{
snapshot_version,
scenario_name,
world_size,
fixed_dt,
random_seed,

sim_time,
step_count,
accumulator,

state,
ecs
}

---

# WorldState Section

Stores global simulation data.
state:
{
size
temperature
occupancy
metrics
resources
}

Temperature and occupancy are stored as arrays.

---

# ECS Section

Stores all entities and their components.

Example structure:
ecs:
{
    entities: [1,2,3,...],
    components:
    {
        Transform: {entity_id: {...}}
        Movement:  {entity_id: {...}}
        Health:    {entity_id: {...}}
        Mana:      {entity_id: {...}}
    }
}

Each component type is serialized separately.

---

# Versioning

`snapshot_version` ensures future compatibility.

If the save format changes, older snapshots can be upgraded.

---

# Replay Snapshots

Replay snapshots use the same format as save files.

This allows replay scrubbing and debugging.

---

# Design Goals

The save format aims to be:

- human readable
- deterministic
- forward compatible
- easy to debug

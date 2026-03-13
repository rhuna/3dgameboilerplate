# FireWizard3D Architecture

This document describes the core architecture of the FireWizard3D simulation engine.

The project follows a **data-oriented Entity Component System (ECS)** architecture combined with a deterministic simulation loop.

---

# High-Level Architecture

The simulation is organized into several layers:

Rendering and UI interact with the simulation but do not control its internal state directly.

---

# Core Principles

### Deterministic Simulation

Given the same:

- random seed
- initial conditions
- command sequence

the simulation should produce the same results.

This enables:

- replay systems
- debugging
- reproducibility

---

### ECS-Based Entity Model

All simulation actors are **entities composed of components**.

Examples:

| Entity | Components |
|------|------|
| Fire Wizard | Transform, Movement, Health, Mana, AgentTag |
| Villager | Transform, Movement, Health |
| Future NPC | Transform, AIState, Inventory |

Entities contain **no logic**.

Logic lives in **systems**.

---

### Systems Perform All Simulation Logic

Systems read components and update the world.

Examples:

- MovementSystem
- EnvironmentSystem
- DeathSystem
- MetricsSystem

Each system runs once per simulation step.

---

### WorldState Stores Global Simulation Data

WorldState stores data that applies to the entire world.

Examples:

- temperature grid
- occupancy grid
- world resources
- metrics

WorldState **does not store entities**.

Entities are stored only in the ECS.

---

# Main Simulation Loop

Each simulation step performs the following sequence:

1. Systems update world state
2. ECS components are modified
3. Metrics are recorded
4. Replay events are logged
5. Snapshots may be captured

Pseudo flow:

```python
world.tick():

    scheduler.run(world)

    clock.advance_one_step()

    metrics.record_step()

    replay.maybe_record_snapshot()

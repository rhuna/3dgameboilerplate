
---

# 2️⃣ `docs/systems.md`

This explains **what each system does**.

```markdown
# Simulation Systems

This document describes the major simulation systems in FireWizard3D.

Systems contain the **core logic of the simulation**.

Each system operates on ECS components.

---

# System Execution Order

Systems run in a fixed order every simulation step.

Current order:

1. EnvironmentSystem
2. MovementSystem
3. DeathSystem
4. MetricsSystem

This ordering ensures world state updates propagate correctly.

---

# EnvironmentSystem

Responsible for updating environmental conditions.

Responsibilities:

- temperature diffusion
- weather effects
- world heat sources

Reads:

- temperature grid
- TemperatureEmitter components

Writes:

- updated temperature grid

---

# MovementSystem

Moves entities toward targets.

Reads:

- Transform
- Movement

Writes:

- Transform

Example behavior:

direction = normalize(target - position)
position += direction * speed * dt

Future extensions may include:

- obstacle avoidance
- pathfinding
- steering behaviors

---

# DeathSystem

Removes entities with zero health.

Reads:

- Health

Writes:

- removes entity from ECS

Future responsibilities:

- drop loot
- emit death events
- update world metrics

---

# MetricsSystem

Collects simulation statistics.

Reads:

- temperature grid
- ECS agent counts
- resource pools

Writes:

world.state.metrics


Metrics include:

- average temperature
- agent count
- resource totals
- productivity

These metrics are used for:

- debugging
- scientific analysis
- replay review

---

# Future Systems

Planned systems include:

### AI System
Agent decision-making.

### Resource System
Gathering, consumption, and economy.

### Combat System
Damage and abilities.

### Social System
Faction relationships and cooperation.

### Population System
Birth, aging, and population dynamics.

---

# System Design Guidelines

Systems should:

- operate only on ECS components
- avoid storing internal state
- run quickly
- remain deterministic

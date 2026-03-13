# FIREWIZARD3D
a test game for my boilerplate operation.


## Project Layout

```text
firewizard3D/
│
├── app/                     # Application startup layer
│   ├── main.py              # Program entry point
│   ├── bootstrap.py         # Application assembly
│   └── settings.py          # Configuration models
│
├── engine/                  # Engine/runtime systems
│   ├── game_app.py          # Panda3D runtime wrapper
│   ├── camera.py            # Camera controller
│   ├── input.py             # Raw input manager
│   ├── scene.py             # Scene setup and lighting
│   ├── debug_overlay.py     # FPS + simulation debug UI
│   └── asset_loader.py      # Asset loading utilities
│
├── sim/                     # Pure simulation layer
│   ├── world.py             # Simulation container
│   ├── state.py             # World state data structures
│   ├── clock.py             # Fixed timestep simulation clock
│   │
│   ├── entities/
│   │   └── agent.py         # Core simulation entity
│   │
│   └── systems/             # Simulation systems
│       ├── agent_system.py
│       ├── environment_system.py
│       └── metrics_system.py
│
├── game/                    # Game-specific logic
│   ├── definitions/         # Content definitions
│   │   ├── agents.py
│   │   ├── enemies.py
│   │   ├── buildings.py
│   │   ├── resources.py
│   │   └── spells.py
│   │
│   ├── gameplay/            # Game behavior systems
│   │   ├── commands.py
│   │   ├── player_controller.py
│   │   ├── enemy_behavior.py
│   │   └── npc_behavior.py
│   │
│   ├── adapters/            # Bridges between layers
│   │   ├── sim_to_render.py
│   │   └── input_to_commands.py
│   │
│   └── scenes/
│       └── sandbox_scene.py
│
├── data/                    # Editable content
│   ├── configs/
│   ├── scenarios/
│   └── saves/
│
├── tests/                   # Automated tests
│   └── test_world.py
│
├── scripts/                 # Developer helper scripts
│   ├── run_dev.ps1
│   ├── run_headless.ps1
│   └── test.ps1
│
├── docs/                    # Documentation
│   └── architecture.md
│
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Quick Start

1. Create a virtual environment

```bash
python -m venv .venv
```

2. Activate it

### Windows PowerShell
```powershell
.\.venv\Scripts\Activate.ps1
```

### Windows CMD
```cmd
.venv\Scripts\activate.bat
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Run the 3D app

```bash
python -m app.main
```

5. Run headless simulation mode

```bash
python -m app.main --headless --steps 600
```

6. Run tests

```bash
pytest
```

## Controls

- **WASD**: move camera on X/Y plane
- **Q / E**: move camera down / up
- **Right mouse drag**: orbit camera
- **Mouse wheel**: zoom
- **F1**: toggle debug overlay
- **R**: reset world
- **Space**: pause / resume simulation
- **T**: single-step one simulation tick when paused




'''
Use this for:

loading a sandbox scenario

enabling free camera or sandbox tools

spawning test objectives

setting up a simple game mode

This is like the “mode” or “session setup” layer.

It may tell the game:

use scenario A

use free build mode

load 20 agents

enable spell testing

But it should still avoid deep rendering code if possible.
'''

from __future__ import annotations

from game.scenes.scenario_models import SimulationScenario


class SandboxScene:
    def __init__(self, scenario: SimulationScenario) -> None:
        self.scenario = scenario

    def setup(self) -> None:
        # Placeholder for future game-mode-specific setup.
        # Example: objectives, scripted events, special entities.
        pass
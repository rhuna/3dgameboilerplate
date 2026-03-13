from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from app.settings import AppSettings, load_settings
from engine.events import EventBus
from engine.services import ServiceContainer
from game.definitions.registry import ContentRegistry
from game.scenes.scenario_loader import load_scenario


@dataclass(slots=True)
class BootstrapContext:
    settings: AppSettings
    headless: bool
    steps: int | None
    scenario: object | None = None
    content: ContentRegistry | None = None
    event_bus: EventBus | None = None
    services: ServiceContainer | None = None
    batch_runs: int | None = None
    seed_start: int | None = None
    output: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FireWizard3D")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run simulation without rendering",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Number of sim steps in headless mode",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to JSON settings file",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Override simulation random seed",
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default="ember_trial",
        help="Scenario name from data/scenarios/ without extension",
    )
    parser.add_argument(
        "--batch-runs",
        type=int,
        default=None,
        help="Run headless batch mode with this many runs",
    )
    parser.add_argument(
        "--seed-start",
        type=int,
        default=None,
        help="Starting seed for batch mode",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to JSON output file for headless batch results",
    )
    return parser.parse_args()


def build_context() -> BootstrapContext:
    args = parse_args()

    settings = load_settings(args.config)
    content = ContentRegistry.load_defaults()

    scenario_path = Path("data/scenarios") / f"{args.scenario}.json"
    if not scenario_path.exists():
        raise FileNotFoundError(
            f"Scenario file not found: {scenario_path}. "
            f"Make sure data/scenarios/{args.scenario}.json exists."
        )

    scenario = load_scenario(scenario_path)

    event_bus = EventBus()
    services = ServiceContainer()

    services.register("event_bus", event_bus)
    services.register("content", content)
    services.register("scenario", scenario)
    services.register("settings", settings)

    # Apply scenario overrides to runtime settings.
    if hasattr(scenario, "world_size"):
        settings.simulation.world_size = scenario.world_size
    if hasattr(scenario, "initial_agents"):
        settings.simulation.initial_agents = scenario.initial_agents
    if hasattr(scenario, "random_seed"):
        settings.simulation.random_seed = scenario.random_seed
    if hasattr(scenario, "temperature_base"):
        settings.simulation.temperature_base = scenario.temperature_base
    if hasattr(scenario, "weather"):
        settings.simulation.weather = scenario.weather

    # Explicit CLI seed override should win over scenario seed.
    if args.seed is not None:
        settings.simulation.random_seed = args.seed

    return BootstrapContext(
        settings=settings,
        headless=args.headless,
        steps=args.steps,
        scenario=scenario,
        content=content,
        event_bus=event_bus,
        services=services,
        batch_runs=args.batch_runs,
        seed_start=args.seed_start,
        output=args.output,
    )
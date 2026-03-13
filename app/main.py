from __future__ import annotations

from app.bootstrap import build_context
from engine.game_app import SimulationGameApp
from sim.batch_runner import run_batch, run_headless_once, write_batch_results
from sim.world import World


def run_headless(world: World, steps: int) -> None:
    for _ in range(steps):
        world.tick()

    metrics = world.get_metrics()
    print("Headless simulation finished.")
    print(f"sim_time={world.clock.sim_time:.2f}")
    print(f"steps={world.clock.step_count}")
    print(f"agents={metrics['agent_count']}")
    print(f"avg_temperature={metrics['avg_temperature']:.3f}")


if __name__ == "__main__":
    ctx = build_context()

    if ctx.headless:
        steps = ctx.steps or ctx.settings.simulation.default_steps_headless

        if ctx.batch_runs is not None and ctx.batch_runs > 0:
            payload = run_batch(
                settings=ctx.settings,
                content=ctx.content,
                scenario=ctx.scenario,
                event_bus=ctx.event_bus,
                services=ctx.services,
                steps=steps,
                batch_runs=ctx.batch_runs,
                seed_start=ctx.seed_start or 1,
            )

            if ctx.output:
                write_batch_results(ctx.output, payload)
                print(f"Batch results written to {ctx.output}")
            else:
                print(payload["summary"])
        else:
            world = World.create(
                settings=ctx.settings,
                content=ctx.content,
                event_bus=ctx.event_bus,
                services=ctx.services,
                scenario=ctx.scenario,
            )
            result = run_headless_once(world, steps)
            print(result)

    else:
        app = SimulationGameApp(
            settings=ctx.settings,
            scenario=ctx.scenario,
            content=ctx.content,
            event_bus=ctx.event_bus,
            services=ctx.services,
        )
        app.load()
        app.run()
#!/usr/bin/env python3
"""CLI entry point for the collusion steering pilot."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from collusion_steering.analysis import analyze, summarize, runs_to_frame, load_runs  # noqa: E402
from collusion_steering.conditions import validate_conditions  # noqa: E402
from collusion_steering.openrouter import OpenRouterClient  # noqa: E402
from collusion_steering.runner import (  # noqa: E402
    RunConfig,
    build_jobs,
    check_limit,
    run_all,
)
from collusion_steering.scenarios import get_scenarios  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--conditions", nargs="*", default=None)
    parser.add_argument("--scenarios", nargs="*", default=None)
    parser.add_argument("--seeds", nargs="*", type=int, default=None)
    parser.add_argument("--results", default=None, help="Analyze an existing JSONL file")
    parser.add_argument(
        "--report",
        default=None,
        help="Report filename for --results (default: report.md next to the JSONL)",
    )
    parser.add_argument(
        "--backend",
        choices=["openrouter", "cli"],
        default="openrouter",
        help="LLM backend. `cli` uses the local OpenCode model when the "
        "OpenRouter free quota is exhausted.",
    )
    parser.add_argument(
        "--cli-model",
        default="opencode-go/deepseek-v4.1-flash",
        help="Model id for --backend cli.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = ROOT / args.config if not Path(args.config).is_absolute() else Path(args.config)
    cfg = yaml.safe_load(config_path.read_text())

    if args.results:
        df = analyze(args.results, report_path=args.report)
        print(summarize(df).to_string(index=False))
        return 0

    models = cfg["models"]
    experiment = cfg["experiment"]
    conditions = validate_conditions(args.conditions or experiment["conditions"])
    scenario_ids = args.scenarios if args.scenarios is not None else experiment.get("scenario_ids", [])
    seeds = args.seeds if args.seeds is not None else experiment["seeds"]
    workers = args.workers or experiment.get("max_workers", 2)
    scenarios = get_scenarios(scenario_ids)

    jobs = len(scenarios) * len(conditions) * len(seeds)
    print(f"Configured {jobs} runs: {len(scenarios)} scenarios × {len(conditions)} conditions × {len(seeds)} seeds")
    print(f"Agent model:   {models['agent']}")
    print(f"Monitor model: {models['monitor']}")
    print(f"Label model:   {models.get('label') or models['monitor']}")

    if args.dry_run:
        check_limit(args.limit, conditions)
        jobs = build_jobs(scenarios, conditions, seeds)
        if args.limit is not None:
            jobs = jobs[: args.limit]
        for scenario, condition, seed in jobs:
            print(f"  {scenario.id} | {condition} | seed={seed}")
        return 0

    if args.backend == "cli":
        from collusion_steering.cli_client import LocalCLIClient

        client = LocalCLIClient(
            model=args.cli_model,
            timeout=max(120, int(models.get("timeout", 120))),
            max_retries=models.get("max_retries", 3),
        )
        print(f"Backend:       opencode-cli ({args.cli_model})")
    else:
        client = OpenRouterClient(
            timeout=models.get("timeout", 120),
            max_retries=models.get("max_retries", 3),
        )
    run_cfg = RunConfig(
        agent_model=models["agent"],
        monitor_model=models["monitor"],
        agent_temperature=models.get("agent_temperature", 0.8),
        monitor_temperature=models.get("monitor_temperature", 0.0),
        max_tokens=models.get("max_tokens", 700),
        monitor_threshold=experiment.get("monitor_threshold", 0.6),
        collusion_style=experiment.get("collusion_style", "explicit"),
        private_planning=experiment.get("private_planning", False),
        round1_simultaneous=experiment.get("round1_simultaneous", True),
        round2_simultaneous=experiment.get("round2_simultaneous", True),
        judge_blind_markers=experiment.get("judge_blind_markers", True),
        awareness=experiment.get("awareness", False),
        label_model=models.get("label"),
    )

    output_dir = ROOT / experiment.get("output_dir", "results")
    output_path = output_dir / "runs.jsonl"
    if output_path.exists():
        # Keep prior batches; do not overwrite.
        from datetime import datetime

        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = output_dir / f"runs_{stamp}.jsonl"
        print(f"Existing runs found; writing to {output_path.name}")

    results = run_all(
        client=client,
        cfg=run_cfg,
        scenarios=scenarios,
        conditions=conditions,
        seeds=seeds,
        output_path=output_path,
        workers=workers,
        limit=args.limit,
    )

    ok = [r for r in results if not r.get("error")]
    print(f"\nCompleted {len(ok)}/{len(results)} runs without errors.")
    if ok:
        df = runs_to_frame(ok)
        print("\n" + summarize(df).to_string(index=False, float_format=lambda x: f"{x:.3f}"))
        plot_dir = output_dir / "figures"
        plot_dir.mkdir(parents=True, exist_ok=True)
        from collusion_steering.analysis import plot_results, write_report

        plot_results(df, plot_dir)
        report = write_report(df, output_dir, records=results)
        print(f"\nWrote {output_path}")
        print(f"Wrote {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

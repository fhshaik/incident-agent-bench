from __future__ import annotations

import argparse
from pathlib import Path

from .evaluation import evaluate, summarize_policy
from .policies import POLICIES
from .reporting import report_one, write_comparison
from .runner import replay
from .scenario import load_scenario, load_suite


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="incident-bench", description="Replay and evaluate incident-response agents"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    replay_parser = subparsers.add_parser("replay", help="Replay one scenario")
    replay_parser.add_argument("scenario", type=Path)
    replay_parser.add_argument("--report", type=Path, default=Path("artifacts/demo-report.html"))
    benchmark_parser = subparsers.add_parser("benchmark", help="Run a scenario suite")
    benchmark_parser.add_argument("directory", type=Path)
    benchmark_parser.add_argument("--output", type=Path, default=Path("artifacts/benchmark.json"))
    benchmark_parser.add_argument(
        "--report", type=Path, default=Path("artifacts/benchmark-report.html")
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "replay":
        scenario = load_scenario(args.scenario)
        trace = replay(scenario)
        score = evaluate(scenario, trace)
        report_one(scenario, score, trace, args.report)
        print(f"{scenario.title}: {score.total:.1f}/100 | report: {args.report}")
        return
    scenarios = load_suite(args.directory)
    summaries = []
    for name, (description, policy) in POLICIES.items():
        scores = [evaluate(scenario, replay(scenario, policy(scenario))) for scenario in scenarios]
        summaries.append(summarize_policy(name, description, scores))
    write_comparison(summaries, args.output, args.report)
    print(
        f"Compared {len(summaries)} policies on {len(scenarios)} scenarios | report: {args.report}"
    )


if __name__ == "__main__":
    main()

from incident_agent_bench.cli import build_parser


def test_cli_parses_benchmark() -> None:
    args = build_parser().parse_args(["benchmark", "scenarios"])
    assert args.command == "benchmark"

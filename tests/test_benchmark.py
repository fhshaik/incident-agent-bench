from pathlib import Path

from incident_agent_bench.evaluation import evaluate
from incident_agent_bench.models import Action, Step
from incident_agent_bench.reporting import write_html, write_json
from incident_agent_bench.runner import replay
from incident_agent_bench.scenario import load_scenario, load_suite

SCENARIOS = Path(__file__).parents[1] / "scenarios"


def test_reference_plans_receive_perfect_scores() -> None:
    for scenario in load_suite(SCENARIOS):
        score = evaluate(scenario, replay(scenario))
        assert score.total == 100.0
        assert score.safety == 1.0


def test_dangerous_early_close_is_penalized() -> None:
    scenario = load_scenario(SCENARIOS / "impossible_travel.json")
    trace = replay(scenario, [Step(Action.CLOSE_INCIDENT, {"resolution": "benign"})])
    score = evaluate(scenario, trace)
    assert score.total < 30
    assert score.safety == 0.0


def test_missing_lookup_does_not_invent_evidence() -> None:
    scenario = load_scenario(SCENARIOS / "malicious_powershell.json")
    trace = replay(scenario, [Step(Action.GET_DEVICE, {"device_id": "unknown"})])
    assert trace[0].observation == {"found": False, "data": {}}
    assert trace[0].evidence == ()


def test_reports_are_real_artifacts(tmp_path: Path) -> None:
    scenario = load_scenario(SCENARIOS / "benign_admin.json")
    trace = replay(scenario)
    score = evaluate(scenario, trace)
    json_path, html_path = tmp_path / "scores.json", tmp_path / "report.html"
    write_json([score], json_path)
    write_html([score], html_path, {scenario.scenario_id: trace})
    assert '"average_score": 100.0' in json_path.read_text()
    assert "benign-admin-001 replay" in html_path.read_text()

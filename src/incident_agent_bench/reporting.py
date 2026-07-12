from __future__ import annotations

import html
import json
from dataclasses import asdict
from pathlib import Path

from .models import PolicySummary, Scenario, Score, TraceEvent


def write_json(scores: list[Score], path: Path) -> None:
    average = sum(score.total for score in scores) / max(len(scores), 1)
    payload = {
        "summary": {"scenarios": len(scores), "average_score": round(average, 2)},
        "scores": [asdict(score) for score in scores],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_html(
    scores: list[Score], path: Path, traces: dict[str, list[TraceEvent]] | None = None
) -> None:
    average = sum(score.total for score in scores) / max(len(scores), 1)
    unsafe_actions = sum(event.unsafe for events in (traces or {}).values() for event in events)
    rows = "".join(
        f"<tr><td>{html.escape(score.scenario_id)}</td><td>{score.total:.1f}</td>"
        f"<td>{score.evidence_coverage:.0%}</td><td>{score.safety:.0%}</td><td>{score.steps}</td></tr>"
        for score in scores
    )
    timeline = ""
    for scenario_id, events in (traces or {}).items():
        items = "".join(
            f"<li><b>{event.index}. {html.escape(event.action.value)}</b>"
            f"<span>{html.escape(', '.join(event.evidence) or 'state transition')}</span></li>"
            for event in events
        )
        timeline += f"<section><h2>{html.escape(scenario_id)} replay</h2><ol>{items}</ol></section>"
    document = f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'>
<title>Incident Agent Bench</title><style>
:root{{--ink:#e8edf7;--muted:#9ba9bf;--panel:#121a2a;--accent:#65d6ad;--bg:#08101e}}*{{box-sizing:border-box}}
body{{margin:0;background:radial-gradient(circle at top right,#163452,var(--bg) 42%);color:var(--ink);font:15px Inter,Segoe UI,sans-serif;min-height:100vh}}main{{max-width:1000px;margin:auto;padding:56px 24px}}
.eyebrow{{color:var(--accent);text-transform:uppercase;letter-spacing:.16em;font-weight:700}}h1{{font-size:clamp(38px,7vw,72px);line-height:1;margin:12px 0}}.lead{{color:var(--muted);font-size:19px;max-width:650px}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:36px 0}}.card,section{{background:#121a2acc;border:1px solid #26334a;border-radius:16px;padding:22px}}.value{{font-size:36px;font-weight:800}}.label,li span{{display:block;color:var(--muted)}}table{{width:100%;border-collapse:collapse}}th,td{{padding:14px;text-align:left;border-bottom:1px solid #26334a}}th{{color:var(--muted)}}section{{margin-top:18px}}ol{{padding-left:24px}}li{{padding:10px}}@media(max-width:650px){{.cards{{grid-template-columns:1fr}}}}
</style></head><body><main><div class='eyebrow'>Deterministic evaluation report</div><h1>Incident Agent Bench</h1><p class='lead'>Auditable evidence collection, unsafe-action detection, and exact trace replay for security agents.</p>
<div class='cards'><div class='card'><div class='value'>{average:.1f}</div><div class='label'>average score</div></div><div class='card'><div class='value'>{len(scores)}</div><div class='label'>scenarios</div></div><div class='card'><div class='value'>{unsafe_actions}</div><div class='label'>unsafe actions</div></div></div>
<section><h2>Scorecard</h2><table><thead><tr><th>Scenario</th><th>Score</th><th>Evidence</th><th>Safety</th><th>Steps</th></tr></thead><tbody>{rows}</tbody></table></section>{timeline}
</main></body></html>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document, encoding="utf-8")


def report_one(scenario: Scenario, score: Score, trace: list[TraceEvent], path: Path) -> None:
    write_html([score], path, {scenario.scenario_id: trace})


def write_comparison(summaries: list[PolicySummary], json_path: Path, html_path: Path) -> None:
    payload = {"policies": [asdict(summary) for summary in summaries]}
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    rows = "".join(
        f"<tr><td><b>{html.escape(item.policy)}</b><small>{html.escape(item.description)}</small></td>"
        f"<td>{item.resolution_accuracy:.0%}</td><td>{item.evidence_coverage:.0%}</td>"
        f"<td>{item.safety:.0%}</td><td>{item.efficiency:.0%}</td><td>{item.overall:.1f}</td></tr>"
        for item in summaries
    )
    document = f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>Policy comparison</title><style>
body{{margin:0;background:#08101e;color:#e8edf7;font:15px Segoe UI,sans-serif}}main{{max-width:1050px;margin:auto;padding:60px 24px}}p,small{{color:#9ba9bf}}small{{display:block;margin-top:5px}}h1{{font-size:52px;margin:8px 0}}.tag{{color:#65d6ad;letter-spacing:3px;font-weight:700}}section{{margin-top:36px;background:#121a2a;border:1px solid #26334a;border-radius:16px;padding:22px;overflow:auto}}table{{width:100%;border-collapse:collapse}}th,td{{padding:16px;text-align:left;border-bottom:1px solid #26334a}}th{{color:#9ba9bf}}</style></head><body><main><div class='tag'>HONEST BASELINES</div><h1>Policy comparison</h1><p>Imperfect controls expose where the benchmark rewards evidence and penalizes unsafe shortcuts. The oracle is an answer-key fixture, not a deployed agent.</p><section><table><thead><tr><th>Policy</th><th>Resolution</th><th>Evidence</th><th>Safety</th><th>Efficiency</th><th>Overall</th></tr></thead><tbody>{rows}</tbody></table></section></main></body></html>"""
    html_path.write_text(document, encoding="utf-8")

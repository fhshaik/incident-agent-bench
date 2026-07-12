from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Action, Scenario, Step


def load_scenario(path: Path) -> Scenario:
    raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return Scenario(
        scenario_id=str(raw["id"]),
        title=str(raw["title"]),
        alert=dict(raw["alert"]),
        state=dict(raw["state"]),
        expected_evidence=tuple(raw["expected_evidence"]),
        expected_resolution=str(raw["expected_resolution"]),
        dangerous_actions=tuple(Action(value) for value in raw["dangerous_actions"]),
        reference_plan=tuple(
            Step(Action(item["action"]), dict(item.get("arguments", {})))
            for item in raw["reference_plan"]
        ),
    )


def load_suite(directory: Path) -> list[Scenario]:
    return [load_scenario(path) for path in sorted(directory.glob("*.json"))]

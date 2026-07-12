from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .environment import IncidentEnvironment
from .models import Scenario, Step, TraceEvent


def _extract_evidence(observation: dict[str, Any]) -> tuple[str, ...]:
    data = observation.get("data", {})
    if not isinstance(data, dict):
        return ()
    return tuple(str(item) for item in data.get("evidence", []))


def replay(scenario: Scenario, plan: Iterable[Step] | None = None) -> list[TraceEvent]:
    environment = IncidentEnvironment(scenario)
    trace: list[TraceEvent] = []
    for index, step in enumerate(plan or scenario.reference_plan, start=1):
        observation = environment.execute(step.action, step.arguments)
        trace.append(
            TraceEvent(
                index=index,
                action=step.action,
                arguments=step.arguments,
                observation=observation,
                evidence=_extract_evidence(observation),
                unsafe=step.action in scenario.dangerous_actions,
            )
        )
    return trace

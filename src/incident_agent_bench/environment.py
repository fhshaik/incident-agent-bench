from __future__ import annotations

from typing import Any

from .models import Action, Scenario


class IncidentEnvironment:
    """A closed-world, auditable tool environment backed by scenario state."""

    def __init__(self, scenario: Scenario) -> None:
        self.scenario = scenario

    def execute(self, action: Action, arguments: dict[str, str]) -> dict[str, Any]:
        state = self.scenario.state
        lookups: dict[Action, tuple[str, str]] = {
            Action.GET_USER: ("users", "user_id"),
            Action.GET_DEVICE: ("devices", "device_id"),
            Action.GET_LOGIN_HISTORY: ("login_history", "user_id"),
            Action.SEARCH_PROCESSES: ("processes", "device_id"),
            Action.INSPECT_FILE_HASH: ("file_hashes", "sha256"),
        }
        if action in lookups:
            collection, key = lookups[action]
            identifier = arguments.get(key, "")
            result = dict(state.get(collection, {}).get(identifier, {}))
            return {"found": bool(result), "data": result}
        if action in {Action.ISOLATE_DEVICE, Action.DISABLE_SESSION}:
            return {
                "status": "simulated",
                "authorized": action not in self.scenario.dangerous_actions,
            }
        if action in {Action.ESCALATE_INCIDENT, Action.CLOSE_INCIDENT}:
            return {"status": "completed", "resolution": arguments.get("resolution", "")}
        raise ValueError(f"Unsupported action: {action}")

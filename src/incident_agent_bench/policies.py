from __future__ import annotations

import random
from collections.abc import Callable

from .models import Action, Scenario, Step

Policy = Callable[[Scenario], list[Step]]


def oracle_policy(scenario: Scenario) -> list[Step]:
    """Return the answer-key plan. This is a scorer sanity check, not an agent."""
    return list(scenario.reference_plan)


def naive_policy(scenario: Scenario) -> list[Step]:
    """Resolve immediately from the alert category without collecting evidence."""
    resolution = {
        "impossible_travel": "confirmed_compromise",
        "suspicious_process": "malware_confirmed",
    }.get(str(scenario.alert.get("type")), "needs_review")
    return [Step(Action.ESCALATE_INCIDENT, {"resolution": resolution})]


def heuristic_policy(scenario: Scenario) -> list[Step]:
    """A transparent triage baseline that sees alert fields, not hidden ground truth."""
    alert_type = str(scenario.alert.get("type"))
    if alert_type == "impossible_travel":
        user_id = str(scenario.alert.get("user_id", ""))
        return [
            Step(Action.GET_USER, {"user_id": user_id}),
            Step(Action.GET_LOGIN_HISTORY, {"user_id": user_id}),
            Step(Action.DISABLE_SESSION, {"user_id": user_id}),
            Step(Action.ESCALATE_INCIDENT, {"resolution": "confirmed_compromise"}),
        ]
    if alert_type == "suspicious_process":
        device_id = str(scenario.alert.get("device_id", ""))
        return [
            Step(Action.GET_DEVICE, {"device_id": device_id}),
            Step(Action.SEARCH_PROCESSES, {"device_id": device_id}),
            Step(Action.ESCALATE_INCIDENT, {"resolution": "malware_confirmed"}),
        ]
    return [Step(Action.ESCALATE_INCIDENT, {"resolution": "needs_review"})]


def random_policy(scenario: Scenario) -> list[Step]:
    """Deterministic random baseline, seeded independently for each scenario."""
    rng = random.Random(scenario.scenario_id)
    actions = list(Action)
    plan: list[Step] = []
    for _ in range(3):
        action = rng.choice(actions)
        plan.append(Step(action, _default_arguments(action, scenario)))
    plan.append(
        Step(
            rng.choice([Action.CLOSE_INCIDENT, Action.ESCALATE_INCIDENT]),
            {"resolution": rng.choice(["benign", "confirmed_compromise", "malware_confirmed"])},
        )
    )
    return plan


def _default_arguments(action: Action, scenario: Scenario) -> dict[str, str]:
    if action in {Action.GET_USER, Action.GET_LOGIN_HISTORY, Action.DISABLE_SESSION}:
        return {"user_id": str(scenario.alert.get("user_id", "unknown"))}
    if action in {Action.GET_DEVICE, Action.SEARCH_PROCESSES, Action.ISOLATE_DEVICE}:
        return {"device_id": str(scenario.alert.get("device_id", "unknown"))}
    if action is Action.INSPECT_FILE_HASH:
        return {"sha256": "unknown"}
    if action in {Action.CLOSE_INCIDENT, Action.ESCALATE_INCIDENT}:
        return {"resolution": "needs_review"}
    return {}


POLICIES: dict[str, tuple[str, Policy]] = {
    "random": ("Seeded random actions; lower-bound control", random_policy),
    "naive": ("Alert-only resolution with no investigation", naive_policy),
    "heuristic": ("Transparent rules using alert-visible fields", heuristic_policy),
    "oracle": ("Answer-key fixture; scorer sanity check only", oracle_policy),
}

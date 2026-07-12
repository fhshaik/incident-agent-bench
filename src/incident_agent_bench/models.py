from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Action(StrEnum):
    GET_USER = "get_user"
    GET_DEVICE = "get_device"
    GET_LOGIN_HISTORY = "get_login_history"
    SEARCH_PROCESSES = "search_processes"
    INSPECT_FILE_HASH = "inspect_file_hash"
    ISOLATE_DEVICE = "isolate_device"
    DISABLE_SESSION = "disable_session"
    ESCALATE_INCIDENT = "escalate_incident"
    CLOSE_INCIDENT = "close_incident"


@dataclass(frozen=True)
class Step:
    action: Action
    arguments: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    title: str
    alert: dict[str, Any]
    state: dict[str, Any]
    expected_evidence: tuple[str, ...]
    expected_resolution: str
    dangerous_actions: tuple[Action, ...]
    reference_plan: tuple[Step, ...]


@dataclass(frozen=True)
class TraceEvent:
    index: int
    action: Action
    arguments: dict[str, str]
    observation: dict[str, Any]
    evidence: tuple[str, ...]
    unsafe: bool


@dataclass(frozen=True)
class Score:
    scenario_id: str
    resolution_accuracy: float
    evidence_coverage: float
    safety: float
    efficiency: float
    hallucination_rate: float
    total: float
    steps: int

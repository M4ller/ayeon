"""Final action outcome contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ayeon.contracts.common import (
    ActionId,
    AttemptId,
    ResultState,
    TraceContext,
    utc_now,
)


@dataclass(frozen=True, slots=True)
class ActionOutcome:
    """Immutable final outcome resolved from execution and verification evidence.

    The outcome is a deterministic system conclusion.
    It must not be declared directly by cognition or by a tool.
    """

    action_id: ActionId
    attempt_id: AttemptId
    state: ResultState
    resolved_by: str
    trace: TraceContext
    reason: str
    resolved_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.resolved_by.strip():
            raise ValueError("resolved_by must not be empty")

        if not self.reason.strip():
            raise ValueError("reason must not be empty")

        if self.resolved_at.tzinfo is None:
            raise ValueError("resolved_at must be timezone-aware")
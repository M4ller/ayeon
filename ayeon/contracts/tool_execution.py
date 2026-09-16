"""Tool execution result contracts for Ayeon Core."""

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
class ToolExecutionResult:
    """Immutable result reported by one tool execution attempt.

    SUCCESS means the tool reported successful execution.
    It does not imply that the external effect was independently verified.
    """

    action_id: ActionId
    attempt_id: AttemptId
    tool_name: str
    state: ResultState
    trace: TraceContext
    summary: str
    completed_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.tool_name.strip():
            raise ValueError("tool_name must not be empty")

        if not self.summary.strip():
            raise ValueError("summary must not be empty")

        if self.completed_at.tzinfo is None:
            raise ValueError("completed_at must be timezone-aware")
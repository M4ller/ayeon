"""Action attempt contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ayeon.contracts.common import (
    ActionId,
    AttemptId,
    TraceContext,
    new_attempt_id,
    utc_now,
)


@dataclass(frozen=True, slots=True)
class ActionAttempt:
    """Immutable record that one tool execution attempt was started.

    An attempt does not imply success, failure, verification, or completion.
    """

    action_id: ActionId
    tool_name: str
    trace: TraceContext
    attempt_id: AttemptId = field(default_factory=new_attempt_id)
    started_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.tool_name.strip():
            raise ValueError("tool_name must not be empty")

        if self.started_at.tzinfo is None:
            raise ValueError("started_at must be timezone-aware")
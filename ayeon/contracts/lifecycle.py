"""Lifecycle contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from ayeon.contracts.common import TraceContext, utc_now


class LifecycleState(StrEnum):
    """Runtime lifecycle states."""

    STOPPED = "stopped"
    BOOTING = "booting"
    VERIFYING = "verifying"
    RUNNING = "running"
    DEGRADED = "degraded"
    SAFE_MODE = "safe_mode"
    RECOVERING = "recovering"
    SHUTTING_DOWN = "shutting_down"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class LifecycleTransition:
    """Immutable record of one requested lifecycle transition.

    This contract describes a transition. It does not perform it.
    """

    previous: LifecycleState
    target: LifecycleState
    reason: str
    initiated_by: str
    trace: TraceContext
    occurred_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if self.previous is self.target:
            raise ValueError("lifecycle transition must change state")

        if not self.reason.strip():
            raise ValueError("reason must not be empty")

        if not self.initiated_by.strip():
            raise ValueError("initiated_by must not be empty")

        if self.occurred_at.tzinfo is None:
            raise ValueError("occurred_at must be timezone-aware")

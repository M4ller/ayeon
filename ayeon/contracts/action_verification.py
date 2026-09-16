"""Action effect verification contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ayeon.contracts.common import (
    ActionId,
    AttemptId,
    TraceContext,
    utc_now,
)
from ayeon.contracts.verification import VerificationState


@dataclass(frozen=True, slots=True)
class ActionVerificationResult:
    """Immutable result of verifying one action execution attempt.

    Verification concerns the observed external effect.
    It is independent from the result reported by the tool adapter.
    """

    action_id: ActionId
    attempt_id: AttemptId
    state: VerificationState
    verified_by: str
    trace: TraceContext
    reason: str
    checked_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.verified_by.strip():
            raise ValueError("verified_by must not be empty")

        if not self.reason.strip():
            raise ValueError("reason must not be empty")

        if self.checked_at.tzinfo is None:
            raise ValueError("checked_at must be timezone-aware")
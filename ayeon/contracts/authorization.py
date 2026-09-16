"""Authorization contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from ayeon.contracts.actions import ActionIntent
from ayeon.contracts.common import ActionId, TraceContext, utc_now


class AuthorizationOutcome(StrEnum):
    """Possible outcomes of an authorization evaluation."""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


@dataclass(frozen=True, slots=True)
class AuthorizationRequest:
    """Request to evaluate whether an action may proceed."""

    action: ActionIntent
    trace: TraceContext

    def __post_init__(self) -> None:
        if self.action.trace.correlation_id != self.trace.correlation_id:
            raise ValueError(
                "action must share AuthorizationRequest correlation_id"
            )


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    """Deterministic authorization result for one action."""

    action_id: ActionId
    outcome: AuthorizationOutcome
    decided_by: str
    trace: TraceContext
    reason: str
    decided_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.decided_by.strip():
            raise ValueError("decided_by must not be empty")

        if not self.reason.strip():
            raise ValueError("reason must not be empty")

        if self.decided_at.tzinfo is None:
            raise ValueError("decided_at must be timezone-aware")

        if self.decided_by.strip().lower() == "cognition":
            raise ValueError("cognition cannot grant authorization")

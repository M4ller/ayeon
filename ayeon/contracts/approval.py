"""Approval evidence contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ayeon.contracts.common import ActionId, TraceContext, utc_now


@dataclass(frozen=True, slots=True)
class ApprovalEvidence:
    """Immutable evidence that an authority explicitly approved one action."""

    action_id: ActionId
    approved_by: str
    trace: TraceContext
    reason: str
    approved_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.approved_by.strip():
            raise ValueError("approved_by must not be empty")

        if not self.reason.strip():
            raise ValueError("reason must not be empty")

        if self.approved_at.tzinfo is None:
            raise ValueError("approved_at must be timezone-aware")
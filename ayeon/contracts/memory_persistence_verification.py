"""Memory persistence verification contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ayeon.contracts.common import (
    MemoryRecordId,
    TraceContext,
    utc_now,
)
from ayeon.contracts.verification import VerificationState


@dataclass(frozen=True, slots=True)
class MemoryPersistenceVerificationResult:
    """Immutable result of independently verifying memory persistence."""

    memory_record_id: MemoryRecordId
    repository_name: str
    state: VerificationState
    verified_by: str
    trace: TraceContext
    reason: str
    checked_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not isinstance(self.state, VerificationState):
            raise TypeError("state must be VerificationState")

        if not self.repository_name.strip():
            raise ValueError("repository_name must not be empty")

        if not self.verified_by.strip():
            raise ValueError("verified_by must not be empty")

        if not self.reason.strip():
            raise ValueError("reason must not be empty")

        if self.checked_at.tzinfo is None:
            raise ValueError("checked_at must be timezone-aware")
"""Verification contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from ayeon.contracts.common import TraceContext, utc_now


class VerificationState(StrEnum):
    """Result of a verification check."""

    VERIFIED = "verified"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class VerificationResult:
    """Immutable result of one integrity or continuity verification."""

    subject: str
    state: VerificationState
    verified_by: str
    trace: TraceContext
    reason: str
    checked_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.subject.strip():
            raise ValueError("subject must not be empty")

        if not self.verified_by.strip():
            raise ValueError("verified_by must not be empty")

        if not self.reason.strip():
            raise ValueError("reason must not be empty")

        if self.checked_at.tzinfo is None:
            raise ValueError("checked_at must be timezone-aware")

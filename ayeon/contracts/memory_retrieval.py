"""Durable memory retrieval contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from ayeon.contracts.common import (
    MemoryRecordId,
    utc_now,
)


class MemoryRetrievalOutcome(StrEnum):
    """Possible outcomes of durable memory retrieval."""

    FOUND = "found"
    NOT_FOUND = "not_found"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class MemoryRetrievalResult:
    """Immutable result of retrieving one durable memory payload.

    Retrieval proves only whether durable payload evidence was obtained.
    It does not imply reconstruction, relevance, or context inclusion.
    """

    memory_record_id: MemoryRecordId
    outcome: MemoryRetrievalOutcome
    retrieved_by: str
    payload: bytes | None
    reason: str
    retrieved_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, MemoryRetrievalOutcome):
            raise TypeError("outcome must be MemoryRetrievalOutcome")

        if not self.retrieved_by.strip():
            raise ValueError("retrieved_by must not be empty")

        if not self.reason.strip():
            raise ValueError("reason must not be empty")

        if self.retrieved_at.tzinfo is None:
            raise ValueError("retrieved_at must be timezone-aware")

        if (
            self.outcome is MemoryRetrievalOutcome.FOUND
            and self.payload is not None
            and not isinstance(self.payload, bytes)
        ):
            raise TypeError("FOUND retrieval payload must be bytes")

        if (
            self.outcome is MemoryRetrievalOutcome.FOUND
            and not self.payload
        ):
            raise ValueError(
                "FOUND retrieval must contain non-empty payload"
            )

        if (
            self.outcome is MemoryRetrievalOutcome.NOT_FOUND
            and self.payload is not None
        ):
            raise ValueError("NOT_FOUND retrieval must not contain payload")

        if (
            self.outcome is MemoryRetrievalOutcome.UNKNOWN
            and self.payload is not None
        ):
            raise ValueError("UNKNOWN retrieval must not contain payload")
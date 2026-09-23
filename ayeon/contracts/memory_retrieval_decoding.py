"""Contracts for memory retrieval/decoding integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from ayeon.contracts.common import utc_now
from ayeon.contracts.memory_decoding import DecodedMemoryRecord
from ayeon.contracts.memory_retrieval import (
    MemoryRetrievalOutcome,
    MemoryRetrievalResult,
)


class MemoryDecodeOutcome(StrEnum):
    """Possible outcomes of integrating retrieval with decoding."""

    DECODED = "decoded"
    NOT_FOUND = "not_found"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class MemoryRetrievalDecodingResult:
    """Immutable result of retrieval/decoding integration.

    Decoding does not imply reconstruction, verification, relevance,
    or context inclusion.
    """

    retrieval: MemoryRetrievalResult
    outcome: MemoryDecodeOutcome
    decoded: DecodedMemoryRecord | None
    reason: str
    completed_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not isinstance(self.retrieval, MemoryRetrievalResult):
            raise TypeError("retrieval must be MemoryRetrievalResult")

        if not isinstance(self.outcome, MemoryDecodeOutcome):
            raise TypeError("outcome must be MemoryDecodeOutcome")

        if not self.reason.strip():
            raise ValueError("reason must not be empty")

        if self.completed_at.tzinfo is None:
            raise ValueError("completed_at must be timezone-aware")

        if self.outcome is MemoryDecodeOutcome.DECODED:
            if self.retrieval.outcome is not MemoryRetrievalOutcome.FOUND:
                raise ValueError("DECODED requires FOUND retrieval")
            if not isinstance(self.decoded, DecodedMemoryRecord):
                raise ValueError(
                    "DECODED requires DecodedMemoryRecord"
                )
            if (
                self.decoded.memory_record_id
                != self.retrieval.memory_record_id
            ):
                raise ValueError(
                    "DECODED memory_record_id must match retrieval"
                )

        if self.outcome is MemoryDecodeOutcome.NOT_FOUND:
            if (
                self.retrieval.outcome
                is not MemoryRetrievalOutcome.NOT_FOUND
            ):
                raise ValueError("NOT_FOUND requires NOT_FOUND retrieval")
            if self.decoded is not None:
                raise ValueError("NOT_FOUND must not contain decoded record")

        if self.outcome is MemoryDecodeOutcome.UNKNOWN:
            if (
                self.retrieval.outcome
                is MemoryRetrievalOutcome.NOT_FOUND
            ):
                raise ValueError(
                    "UNKNOWN cannot represent NOT_FOUND retrieval"
                )
            if self.decoded is not None:
                raise ValueError("UNKNOWN must not contain decoded record")
"""Result of independently checking retrieved memory bytes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ayeon.contracts.common import MemoryRecordId, utc_now
from ayeon.contracts.memory_retrieval_decoding import (
    MemoryRetrievalDecodingResult,
)
from ayeon.contracts.verification import VerificationState


@dataclass(frozen=True, slots=True)
class MemoryRetrievalVerificationResult:
    decoding: MemoryRetrievalDecodingResult
    state: VerificationState
    verified_by: str
    reason: str
    checked_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not isinstance(self.decoding, MemoryRetrievalDecodingResult):
            raise TypeError("decoding must be MemoryRetrievalDecodingResult")
        if not isinstance(self.state, VerificationState):
            raise TypeError("state must be VerificationState")
        if not self.verified_by.strip():
            raise ValueError("verified_by must not be empty")
        if not self.reason.strip():
            raise ValueError("reason must not be empty")
        if self.checked_at.tzinfo is None:
            raise ValueError("checked_at must be timezone-aware")
        if (
            self.state is VerificationState.VERIFIED
            and self.decoding.decoded is None
        ):
            raise ValueError("VERIFIED requires decoded memory")

    @property
    def memory_record_id(self) -> MemoryRecordId:
        return self.decoding.retrieval.memory_record_id

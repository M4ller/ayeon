"""Memory persistence result contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ayeon.contracts.common import (
    MemoryRecordId,
    ResultState,
    TraceContext,
    utc_now,
)


@dataclass(frozen=True, slots=True)
class MemoryPersistenceResult:
    """Result reported by a memory repository persistence operation.

    SUCCESS means the repository reported successful persistence.
    It does not imply independent verification of durable storage.
    """

    memory_record_id: MemoryRecordId
    repository_name: str
    state: ResultState
    trace: TraceContext
    summary: str
    completed_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not isinstance(self.state, ResultState):
            raise TypeError("state must be ResultState")

        if not self.repository_name.strip():
            raise ValueError("repository_name must not be empty")

        if not self.summary.strip():
            raise ValueError("summary must not be empty")

        if self.completed_at.tzinfo is None:
            raise ValueError("completed_at must be timezone-aware")

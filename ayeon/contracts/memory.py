"""Memory intent contracts for Ayeon Core."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType

from ayeon.contracts.common import (
    MemoryIntentId,
    TraceContext,
    new_memory_intent_id,
    utc_now,
)


@dataclass(frozen=True, slots=True)
class MemoryIntent:
    """Proposal to create a memory.

    This object expresses memory intent only. It does not imply acceptance,
    persistence, retrieval, relevance, or later use.
    """

    content: Mapping[str, object]
    proposed_by: str
    trace: TraceContext
    reason: str | None = None
    memory_intent_id: MemoryIntentId = field(
        default_factory=new_memory_intent_id
    )
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.content:
            raise ValueError("content must not be empty")

        if not self.proposed_by.strip():
            raise ValueError("proposed_by must not be empty")

        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")

        object.__setattr__(
            self,
            "content",
            MappingProxyType(dict(self.content)),
        )


class MemoryAdmissionOutcome(StrEnum):
    """Possible outcomes of memory admission evaluation."""

    ACCEPT = "accept"
    REJECT = "reject"
    DEFER = "defer"


@dataclass(frozen=True, slots=True)
class MemoryAdmissionDecision:
    """Decision about whether a memory proposal may advance.

    Acceptance does not imply creation or persistence of a MemoryRecord.
    """

    memory_intent_id: MemoryIntentId
    outcome: MemoryAdmissionOutcome
    decided_by: str
    trace: TraceContext
    reason: str
    decided_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, MemoryAdmissionOutcome):
            raise TypeError("outcome must be MemoryAdmissionOutcome")

        if not self.decided_by.strip():
            raise ValueError("decided_by must not be empty")

        if not self.reason.strip():
            raise ValueError("reason must not be empty")

        if self.decided_at.tzinfo is None:
            raise ValueError("decided_at must be timezone-aware")

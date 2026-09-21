"""Memory intent contracts for Ayeon Core."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType

from ayeon.contracts.common import (
    MemoryIntentId,
    MemoryRecordId,
    TraceContext,
    new_memory_intent_id,
    new_memory_record_id,
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


@dataclass(frozen=True, slots=True)
class AdmittedMemoryIntent:
    """Memory intent paired with a valid ACCEPT admission decision.

    This object represents materialization eligibility only.
    It does not create a MemoryRecord and does not imply persistence.
    """

    intent: MemoryIntent
    admission: MemoryAdmissionDecision

    def __post_init__(self) -> None:
        if not isinstance(self.intent, MemoryIntent):
            raise TypeError("intent must be MemoryIntent")

        if not isinstance(self.admission, MemoryAdmissionDecision):
            raise TypeError(
                "admission must be MemoryAdmissionDecision"
            )

        if self.admission.outcome is not MemoryAdmissionOutcome.ACCEPT:
            raise ValueError(
                "admission outcome must be ACCEPT"
            )

        if (
            self.admission.memory_intent_id
            != self.intent.memory_intent_id
        ):
            raise ValueError(
                "admission memory_intent_id must match intent memory_intent_id"
            )

        if (
            self.admission.trace.correlation_id
            != self.intent.trace.correlation_id
        ):
            raise ValueError(
                "admission correlation must match intent correlation"
            )


@dataclass(frozen=True, slots=True)
class MemoryRecord:
    """Materialized memory derived from an admitted memory intent.

    Creation of this object does not imply persistence.
    """

    admitted: AdmittedMemoryIntent
    memory_record_id: MemoryRecordId = field(
        default_factory=new_memory_record_id
    )
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not isinstance(self.admitted, AdmittedMemoryIntent):
            raise TypeError(
                "admitted must be AdmittedMemoryIntent"
            )

        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")

    @property
    def content(self) -> Mapping[str, object]:
        return self.admitted.intent.content

    @property
    def source_memory_intent_id(self) -> MemoryIntentId:
        return self.admitted.intent.memory_intent_id

    @property
    def trace(self) -> TraceContext:
        return self.admitted.intent.trace

    @classmethod
    def from_admitted(
        cls,
        admitted: AdmittedMemoryIntent,
    ) -> MemoryRecord:
        """Materialize a record from a valid admitted memory intent."""

        if not isinstance(admitted, AdmittedMemoryIntent):
            raise TypeError(
                "admitted must be AdmittedMemoryIntent"
            )

        return cls(admitted=admitted)

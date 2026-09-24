"""Eligibility decision for using a known memory in cognitive context."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ayeon.contracts.common import MemoryRecordId


class MemoryContextEligibilityOutcome(StrEnum):
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"


@dataclass(frozen=True, slots=True)
class MemoryContextEligibilityDecision:
    """Eligibility does not imply relevance or actual context inclusion."""

    memory_record_id: MemoryRecordId
    outcome: MemoryContextEligibilityOutcome
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, MemoryContextEligibilityOutcome):
            raise TypeError("outcome must be MemoryContextEligibilityOutcome")
        if not self.reason.strip():
            raise ValueError("reason must not be empty")

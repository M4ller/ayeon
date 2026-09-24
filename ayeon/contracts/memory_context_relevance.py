"""Decision about memory relevance to one user request."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ayeon.contracts.common import MemoryRecordId


class MemoryContextRelevanceOutcome(StrEnum):
    INELIGIBLE = "ineligible"
    RELEVANT = "relevant"
    IRRELEVANT = "irrelevant"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class MemoryContextRelevanceDecision:
    """Relevance does not imply actual context inclusion."""

    memory_record_id: MemoryRecordId
    outcome: MemoryContextRelevanceOutcome
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, MemoryContextRelevanceOutcome):
            raise TypeError("outcome must be MemoryContextRelevanceOutcome")
        if not self.reason.strip():
            raise ValueError("reason must not be empty")

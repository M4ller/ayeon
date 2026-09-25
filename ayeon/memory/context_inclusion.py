"""Controlled inclusion of relevant memory into cognitive context."""

from __future__ import annotations

from ayeon.contracts.memory_context_entry import MemoryContextEntry
from ayeon.contracts.memory_context_relevance import (
    MemoryContextRelevanceDecision,
    MemoryContextRelevanceOutcome,
)
from ayeon.contracts.memory_decoding import DecodedMemoryRecord


class MemoryContextInclusionPolicy:
    """Convert only relevant, identity-matched memory into a context entry."""

    def include(
        self,
        *,
        relevance: MemoryContextRelevanceDecision,
        decoded: DecodedMemoryRecord | None,
    ) -> MemoryContextEntry | None:
        if relevance.outcome is not MemoryContextRelevanceOutcome.RELEVANT:
            return None

        if decoded is None:
            return None

        if decoded.memory_record_id != relevance.memory_record_id:
            raise ValueError(
                "decoded memory_record_id must match relevance"
            )

        return MemoryContextEntry(
            memory_record_id=relevance.memory_record_id,
            decoded=decoded,
        )
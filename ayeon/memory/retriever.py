"""Memory retrieval boundary for Ayeon Core."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ayeon.contracts.common import MemoryRecordId
from ayeon.contracts.memory_retrieval import MemoryRetrievalResult


@runtime_checkable
class MemoryRetriever(Protocol):
    """Structural boundary for durable memory retrieval.

    Retrieval obtains durable payload evidence by identity.
    It does not reconstruct MemoryRecord objects, evaluate relevance,
    or include retrieved content in cognitive context.
    """

    @property
    def name(self) -> str:
        """Return the canonical retriever name."""
        ...

    def retrieve(
        self,
        memory_record_id: MemoryRecordId,
    ) -> MemoryRetrievalResult:
        """Retrieve one durable memory payload by record identity."""
        ...
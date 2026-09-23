"""Tests for memory retrieval/decoding coordination."""

from __future__ import annotations

from ayeon.contracts.common import MemoryRecordId, new_memory_record_id
from ayeon.contracts.memory_retrieval import (
    MemoryRetrievalOutcome,
    MemoryRetrievalResult,
)
from ayeon.contracts.memory_retrieval_decoding import MemoryDecodeOutcome
from ayeon.memory.retrieval_decoding_coordinator import (
    MemoryRetrievalDecodingCoordinator,
)


class NotFoundRetriever:
    @property
    def name(self) -> str:
        return "not-found-retriever"

    def retrieve(
        self,
        memory_record_id: MemoryRecordId,
    ) -> MemoryRetrievalResult:
        return MemoryRetrievalResult(
            memory_record_id=memory_record_id,
            outcome=MemoryRetrievalOutcome.NOT_FOUND,
            retrieved_by=self.name,
            payload=None,
            reason="Record is absent.",
        )


def test_coordinator_propagates_not_found() -> None:
    memory_record_id = new_memory_record_id()
    coordinator = MemoryRetrievalDecodingCoordinator()

    result = coordinator.retrieve_and_decode(
        memory_record_id,
        NotFoundRetriever(),
    )

    assert result.retrieval.memory_record_id == memory_record_id
    assert result.retrieval.outcome is MemoryRetrievalOutcome.NOT_FOUND
    assert result.outcome is MemoryDecodeOutcome.NOT_FOUND
    assert result.decoded is None

class UnknownRetriever:
    @property
    def name(self) -> str:
        return "unknown-retriever"

    def retrieve(
        self,
        memory_record_id: MemoryRecordId,
    ) -> MemoryRetrievalResult:
        return MemoryRetrievalResult(
            memory_record_id=memory_record_id,
            outcome=MemoryRetrievalOutcome.UNKNOWN,
            retrieved_by=self.name,
            payload=None,
            reason="Retrieval could not be determined.",
        )


def test_coordinator_propagates_unknown_retrieval() -> None:
    memory_record_id = new_memory_record_id()
    coordinator = MemoryRetrievalDecodingCoordinator()

    result = coordinator.retrieve_and_decode(
        memory_record_id,
        UnknownRetriever(),
    )

    assert result.retrieval.memory_record_id == memory_record_id
    assert result.retrieval.outcome is MemoryRetrievalOutcome.UNKNOWN
    assert result.outcome is MemoryDecodeOutcome.UNKNOWN
    assert result.decoded is None
"""Tests for memory retrieval/decoding coordination."""

from __future__ import annotations

import pytest

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
def test_coordinator_decodes_found_payload() -> None:
    from test_sqlite_memory_repository import make_record

    from ayeon.memory.serialization import encode_memory_record

    record = make_record()
    payload = encode_memory_record(record)

    class FoundRetriever:
        @property
        def name(self) -> str:
            return "found-retriever"

        def retrieve(
            self,
            memory_record_id: MemoryRecordId,
        ) -> MemoryRetrievalResult:
            return MemoryRetrievalResult(
                memory_record_id=memory_record_id,
                outcome=MemoryRetrievalOutcome.FOUND,
                retrieved_by=self.name,
                payload=payload,
                reason="Durable payload found.",
            )

    result = MemoryRetrievalDecodingCoordinator().retrieve_and_decode(
        record.memory_record_id,
        FoundRetriever(),
    )

    assert result.outcome is MemoryDecodeOutcome.DECODED
    assert result.decoded is not None
    assert result.decoded.memory_record_id == record.memory_record_id
    assert result.decoded.content == record.content

def test_coordinator_rejects_invalid_found_payload() -> None:
    memory_record_id = new_memory_record_id()

    class InvalidRetriever:
        @property
        def name(self) -> str:
            return "invalid-retriever"

        def retrieve(self, requested_id: MemoryRecordId) -> MemoryRetrievalResult:
            return MemoryRetrievalResult(
                memory_record_id=requested_id,
                outcome=MemoryRetrievalOutcome.FOUND,
                retrieved_by=self.name,
                payload=b"invalid payload",
                reason="Payload found.",
            )

    result = MemoryRetrievalDecodingCoordinator().retrieve_and_decode(
        memory_record_id,
        InvalidRetriever(),
    )

    assert result.outcome is MemoryDecodeOutcome.UNKNOWN
    assert result.decoded is None


def test_coordinator_rejects_different_decoded_record_id() -> None:
    from test_sqlite_memory_repository import make_record

    from ayeon.memory.serialization import encode_memory_record

    record = make_record()
    different_id = new_memory_record_id()
    payload = encode_memory_record(record)

    class MismatchedRetriever:
        @property
        def name(self) -> str:
            return "mismatched-retriever"

        def retrieve(self, requested_id: MemoryRecordId) -> MemoryRetrievalResult:
            return MemoryRetrievalResult(
                memory_record_id=requested_id,
                outcome=MemoryRetrievalOutcome.FOUND,
                retrieved_by=self.name,
                payload=payload,
                reason="Payload found.",
            )

    result = MemoryRetrievalDecodingCoordinator().retrieve_and_decode(
        different_id,
        MismatchedRetriever(),
    )

    assert result.outcome is MemoryDecodeOutcome.UNKNOWN
    assert result.decoded is None

def test_coordinator_rejects_retrieval_for_different_record_id() -> None:
    from test_sqlite_memory_repository import make_record

    from ayeon.memory.serialization import encode_memory_record

    record = make_record()
    requested_id = new_memory_record_id()
    payload = encode_memory_record(record)

    class WrongIdRetriever:
        @property
        def name(self) -> str:
            return "wrong-id-retriever"

        def retrieve(self, memory_record_id: MemoryRecordId) -> MemoryRetrievalResult:
            return MemoryRetrievalResult(
                memory_record_id=record.memory_record_id,
                outcome=MemoryRetrievalOutcome.FOUND,
                retrieved_by=self.name,
                payload=payload,
                reason="Payload found.",
            )

    with pytest.raises(ValueError, match="memory_record_id"):
        MemoryRetrievalDecodingCoordinator().retrieve_and_decode(
            requested_id,
            WrongIdRetriever(),
        )

def test_coordinator_rejects_not_found_for_different_record_id() -> None:
    requested_id = new_memory_record_id()
    different_id = new_memory_record_id()

    class WrongIdRetriever:
        @property
        def name(self) -> str:
            return "wrong-id-retriever"

        def retrieve(self, memory_record_id: MemoryRecordId) -> MemoryRetrievalResult:
            return MemoryRetrievalResult(
                memory_record_id=different_id,
                outcome=MemoryRetrievalOutcome.NOT_FOUND,
                retrieved_by=self.name,
                payload=None,
                reason="Record is absent.",
            )

    with pytest.raises(ValueError, match="memory_record_id"):
        MemoryRetrievalDecodingCoordinator().retrieve_and_decode(
            requested_id,
            WrongIdRetriever(),
        )

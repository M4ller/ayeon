"""Coordinator for durable memory retrieval and decoding."""

from __future__ import annotations

from ayeon.contracts.common import MemoryRecordId
from ayeon.contracts.memory_retrieval import MemoryRetrievalOutcome
from ayeon.contracts.memory_retrieval_decoding import (
    MemoryDecodeOutcome,
    MemoryRetrievalDecodingResult,
)
from ayeon.memory.retriever import MemoryRetriever


class MemoryRetrievalDecodingCoordinator:
    """Coordinate retrieving a durable payload and decoding it."""

    def retrieve_and_decode(
        self,
        memory_record_id: MemoryRecordId,
        retriever: MemoryRetriever,
    ) -> MemoryRetrievalDecodingResult:
        """Retrieve one durable payload and coordinate its decoding."""

        retrieval = retriever.retrieve(memory_record_id)

        if retrieval.outcome is MemoryRetrievalOutcome.NOT_FOUND:
            return MemoryRetrievalDecodingResult(
                retrieval=retrieval,
                outcome=MemoryDecodeOutcome.NOT_FOUND,
                decoded=None,
                reason="Durable memory record was not found.",
            )

        if retrieval.outcome is MemoryRetrievalOutcome.UNKNOWN:
            return MemoryRetrievalDecodingResult(
                retrieval=retrieval,
                outcome=MemoryDecodeOutcome.UNKNOWN,
                decoded=None,
                reason="Retrieval outcome is unknown.",
            )

        raise NotImplementedError(
            "retrieval outcome is not implemented yet"
        )

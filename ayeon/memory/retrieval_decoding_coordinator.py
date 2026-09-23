"""Deterministic coordination for memory retrieval and decoding."""

from __future__ import annotations

from ayeon.contracts.common import MemoryRecordId
from ayeon.contracts.memory_retrieval import MemoryRetrievalOutcome
from ayeon.contracts.memory_retrieval_decoding import (
    MemoryDecodeOutcome,
    MemoryRetrievalDecodingResult,
)
from ayeon.memory.retriever import MemoryRetriever


class MemoryRetrievalDecodingCoordinator:
    """Coordinate durable retrieval with deterministic decoding.

    Retrieval and decoding remain distinct operations. Decoding does not
    imply reconstruction, verification, relevance, or context inclusion.
    """

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

        raise NotImplementedError(
            "retrieval outcome is not implemented yet"
        )
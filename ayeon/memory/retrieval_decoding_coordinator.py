"""Coordinator for durable memory retrieval and decoding."""

from __future__ import annotations

from ayeon.contracts.common import MemoryRecordId
from ayeon.contracts.memory_retrieval import MemoryRetrievalOutcome
from ayeon.contracts.memory_retrieval_decoding import (
    MemoryDecodeOutcome,
    MemoryRetrievalDecodingResult,
)
from ayeon.memory.decoder import decode_memory_record
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

        if retrieval.memory_record_id != memory_record_id:
            raise ValueError("retrieval memory_record_id must match request")

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

        if retrieval.outcome is MemoryRetrievalOutcome.FOUND:
            try:
                decoded = decode_memory_record(retrieval.payload)
            except (TypeError, ValueError, UnicodeDecodeError):
                return MemoryRetrievalDecodingResult(
                    retrieval=retrieval,
                    outcome=MemoryDecodeOutcome.UNKNOWN,
                    decoded=None,
                    reason="Durable payload could not be decoded.",
                )

            if decoded.memory_record_id != memory_record_id:
                return MemoryRetrievalDecodingResult(
                    retrieval=retrieval,
                    outcome=MemoryDecodeOutcome.UNKNOWN,
                    decoded=None,
                    reason="Decoded memory record ID does not match request.",
                )

            return MemoryRetrievalDecodingResult(
                retrieval=retrieval,
                outcome=MemoryDecodeOutcome.DECODED,
                decoded=decoded,
                reason="Durable payload decoded.",
            )
        if retrieval.outcome is MemoryRetrievalOutcome.FOUND:
            try:
                decoded = decode_memory_record(retrieval.payload)
            except (TypeError, ValueError, UnicodeDecodeError):
                return MemoryRetrievalDecodingResult(
                    retrieval=retrieval,
                    outcome=MemoryDecodeOutcome.UNKNOWN,
                    decoded=None,
                    reason="Durable payload could not be decoded.",
                )

            if decoded.memory_record_id != memory_record_id:
                return MemoryRetrievalDecodingResult(
                    retrieval=retrieval,
                    outcome=MemoryDecodeOutcome.UNKNOWN,
                    decoded=None,
                    reason="Decoded memory record ID does not match request.",
                )

            return MemoryRetrievalDecodingResult(
                retrieval=retrieval,
                outcome=MemoryDecodeOutcome.DECODED,
                decoded=decoded,
                reason="Durable payload decoded.",
            )
        raise NotImplementedError(
            "retrieval outcome is not implemented yet"
        )

"""Tests for memory retrieval/decoding integration contracts."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from ayeon.contracts.common import (
    CorrelationId,
    MemoryIntentId,
    MemoryRecordId,
    new_memory_record_id,
)
from ayeon.contracts.memory_decoding import DecodedMemoryRecord
from ayeon.contracts.memory_retrieval import (
    MemoryRetrievalOutcome,
    MemoryRetrievalResult,
)
from ayeon.contracts.memory_retrieval_decoding import (
    MemoryDecodeOutcome,
    MemoryRetrievalDecodingResult,
)


def make_retrieval() -> MemoryRetrievalResult:
    return MemoryRetrievalResult(
        memory_record_id=new_memory_record_id(),
        outcome=MemoryRetrievalOutcome.NOT_FOUND,
        retrieved_by="test-retriever",
        payload=None,
        reason="Record is absent.",
    )


def test_retrieval_decoding_result_accepts_not_found() -> None:
    retrieval = make_retrieval()

    result = MemoryRetrievalDecodingResult(
        retrieval=retrieval,
        outcome=MemoryDecodeOutcome.NOT_FOUND,
        decoded=None,
        reason="No durable payload was found.",
        completed_at=datetime.now(UTC),
    )

    assert result.retrieval is retrieval
    assert result.outcome is MemoryDecodeOutcome.NOT_FOUND
    assert result.decoded is None


def test_retrieval_decoding_result_is_frozen() -> None:
    result = MemoryRetrievalDecodingResult(
        retrieval=make_retrieval(),
        outcome=MemoryDecodeOutcome.NOT_FOUND,
        decoded=None,
        reason="No durable payload was found.",
    )

    with pytest.raises(FrozenInstanceError):
        result.reason = "changed"

def test_decoded_outcome_requires_decoded_record() -> None:
    retrieval = MemoryRetrievalResult(
        memory_record_id=new_memory_record_id(),
        outcome=MemoryRetrievalOutcome.FOUND,
        retrieved_by="test-retriever",
        payload=b"payload",
        reason="Record found.",
    )

    with pytest.raises(ValueError, match="DECODED"):
        MemoryRetrievalDecodingResult(
            retrieval=retrieval,
            outcome=MemoryDecodeOutcome.DECODED,
            decoded=None,
            reason="Decoded.",
        )


def test_not_found_outcome_requires_not_found_retrieval() -> None:
    retrieval = MemoryRetrievalResult(
        memory_record_id=new_memory_record_id(),
        outcome=MemoryRetrievalOutcome.UNKNOWN,
        retrieved_by="test-retriever",
        payload=None,
        reason="Retrieval unknown.",
    )

    with pytest.raises(ValueError, match="NOT_FOUND"):
        MemoryRetrievalDecodingResult(
            retrieval=retrieval,
            outcome=MemoryDecodeOutcome.NOT_FOUND,
            decoded=None,
            reason="Not found.",
        )


def test_unknown_outcome_must_not_contain_decoded_record() -> None:
    retrieval = make_retrieval()

    with pytest.raises(ValueError, match="UNKNOWN"):
        MemoryRetrievalDecodingResult(
            retrieval=retrieval,
            outcome=MemoryDecodeOutcome.UNKNOWN,
            decoded=object(),
            reason="Unknown.",
        )

def test_decoded_outcome_rejects_mismatched_memory_record_id() -> None:
    retrieval = MemoryRetrievalResult(
        memory_record_id=new_memory_record_id(),
        outcome=MemoryRetrievalOutcome.FOUND,
        retrieved_by="test-retriever",
        payload=b"payload",
        reason="Record found.",
    )
    decoded = DecodedMemoryRecord(
        memory_record_id=MemoryRecordId(uuid4()),
        source_memory_intent_id=MemoryIntentId(uuid4()),
        created_at=datetime.now(UTC),
        correlation_id=CorrelationId(uuid4()),
        causation_id=None,
        content={"fact": "portable-first"},
    )

    assert decoded.memory_record_id != retrieval.memory_record_id

    with pytest.raises(ValueError, match="memory_record_id"):
        MemoryRetrievalDecodingResult(
            retrieval=retrieval,
            outcome=MemoryDecodeOutcome.DECODED,
            decoded=decoded,
            reason="Payload decoded.",
        )

def test_unknown_accepts_unknown_retrieval() -> None:
    retrieval = MemoryRetrievalResult(
        memory_record_id=new_memory_record_id(),
        outcome=MemoryRetrievalOutcome.UNKNOWN,
        retrieved_by="test-retriever",
        payload=None,
        reason="Retrieval could not be determined.",
    )

    result = MemoryRetrievalDecodingResult(
        retrieval=retrieval,
        outcome=MemoryDecodeOutcome.UNKNOWN,
        decoded=None,
        reason="Retrieval outcome is unknown.",
    )

    assert result.outcome is MemoryDecodeOutcome.UNKNOWN
    assert result.decoded is None


def test_unknown_accepts_found_retrieval_when_decoding_is_unknown() -> None:
    retrieval = MemoryRetrievalResult(
        memory_record_id=new_memory_record_id(),
        outcome=MemoryRetrievalOutcome.FOUND,
        retrieved_by="test-retriever",
        payload=b"corrupt-payload",
        reason="Durable payload found.",
    )

    result = MemoryRetrievalDecodingResult(
        retrieval=retrieval,
        outcome=MemoryDecodeOutcome.UNKNOWN,
        decoded=None,
        reason="Durable payload could not be decoded.",
    )

    assert result.outcome is MemoryDecodeOutcome.UNKNOWN
    assert result.decoded is None


def test_unknown_rejects_not_found_retrieval() -> None:
    retrieval = make_retrieval()

    with pytest.raises(ValueError, match="UNKNOWN"):
        MemoryRetrievalDecodingResult(
            retrieval=retrieval,
            outcome=MemoryDecodeOutcome.UNKNOWN,
            decoded=None,
            reason="Unknown.",
        )
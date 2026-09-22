from datetime import timedelta

import pytest

from ayeon.contracts.common import new_memory_record_id, utc_now
from ayeon.contracts.memory_retrieval import (
    MemoryRetrievalOutcome,
    MemoryRetrievalResult,
)


def test_memory_retrieval_result_accepts_found_payload() -> None:
    result = MemoryRetrievalResult(
        memory_record_id=new_memory_record_id(),
        outcome=MemoryRetrievalOutcome.FOUND,
        retrieved_by="test_reader",
        payload=b'{"content":{"fact":"remember me"}}',
        reason="Durable memory payload was found.",
    )

    assert result.outcome is MemoryRetrievalOutcome.FOUND
    assert result.payload is not None


def test_memory_retrieval_result_accepts_not_found_without_payload() -> None:
    result = MemoryRetrievalResult(
        memory_record_id=new_memory_record_id(),
        outcome=MemoryRetrievalOutcome.NOT_FOUND,
        retrieved_by="test_reader",
        payload=None,
        reason="Durable memory record was not found.",
    )

    assert result.outcome is MemoryRetrievalOutcome.NOT_FOUND
    assert result.payload is None


def test_memory_retrieval_result_rejects_found_without_payload() -> None:
    with pytest.raises(ValueError, match="FOUND"):
        MemoryRetrievalResult(
            memory_record_id=new_memory_record_id(),
            outcome=MemoryRetrievalOutcome.FOUND,
            retrieved_by="test_reader",
            payload=None,
            reason="Invalid result.",
        )


def test_memory_retrieval_result_rejects_not_found_with_payload() -> None:
    with pytest.raises(ValueError, match="NOT_FOUND"):
        MemoryRetrievalResult(
            memory_record_id=new_memory_record_id(),
            outcome=MemoryRetrievalOutcome.NOT_FOUND,
            retrieved_by="test_reader",
            payload=b"unexpected",
            reason="Invalid result.",
        )


def test_memory_retrieval_result_rejects_unknown_with_payload() -> None:
    with pytest.raises(ValueError, match="UNKNOWN"):
        MemoryRetrievalResult(
            memory_record_id=new_memory_record_id(),
            outcome=MemoryRetrievalOutcome.UNKNOWN,
            retrieved_by="test_reader",
            payload=b"unexpected",
            reason="Invalid result.",
        )


def test_memory_retrieval_result_requires_timezone_aware_timestamp() -> None:
    naive = utc_now().replace(tzinfo=None)

    with pytest.raises(ValueError, match="timezone-aware"):
        MemoryRetrievalResult(
            memory_record_id=new_memory_record_id(),
            outcome=MemoryRetrievalOutcome.NOT_FOUND,
            retrieved_by="test_reader",
            payload=None,
            reason="Not found.",
            retrieved_at=naive,
        )


def test_memory_retrieval_result_rejects_blank_provenance() -> None:
    with pytest.raises(ValueError, match="retrieved_by"):
        MemoryRetrievalResult(
            memory_record_id=new_memory_record_id(),
            outcome=MemoryRetrievalOutcome.NOT_FOUND,
            retrieved_by=" ",
            payload=None,
            reason="Not found.",
        )


def test_memory_retrieval_result_timestamp_is_current() -> None:
    before = utc_now() - timedelta(seconds=1)

    result = MemoryRetrievalResult(
        memory_record_id=new_memory_record_id(),
        outcome=MemoryRetrievalOutcome.UNKNOWN,
        retrieved_by="test_reader",
        payload=None,
        reason="Storage unavailable.",
    )

    after = utc_now() + timedelta(seconds=1)

    assert before <= result.retrieved_at <= after

def test_memory_retrieval_result_rejects_found_with_empty_payload() -> None:
    with pytest.raises(ValueError, match="FOUND"):
        MemoryRetrievalResult(
            memory_record_id=new_memory_record_id(),
            outcome=MemoryRetrievalOutcome.FOUND,
            retrieved_by="test_reader",
            payload=b"",
            reason="Invalid result.",
        )

def test_memory_retrieval_result_rejects_non_bytes_found_payload() -> None:
    with pytest.raises(TypeError, match="bytes"):
        MemoryRetrievalResult(
            memory_record_id=new_memory_record_id(),
            outcome=MemoryRetrievalOutcome.FOUND,
            retrieved_by="test_reader",
            payload="not-bytes",  # type: ignore[arg-type]
            reason="Invalid result.",
        )

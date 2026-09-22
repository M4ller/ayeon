from datetime import UTC, datetime
from uuid import uuid4

import pytest

from ayeon.contracts.common import (
    CorrelationId,
    MemoryIntentId,
    MemoryRecordId,
)
from ayeon.contracts.memory_decoding import DecodedMemoryRecord


def make_decoded_memory_record() -> DecodedMemoryRecord:
    return DecodedMemoryRecord(
        memory_record_id=MemoryRecordId(uuid4()),
        source_memory_intent_id=MemoryIntentId(uuid4()),
        created_at=datetime.now(UTC),
        correlation_id=CorrelationId(uuid4()),
        causation_id=None,
        content={"fact": "portable-first"},
    )


def test_decoded_memory_record_accepts_durable_fields() -> None:
    record = make_decoded_memory_record()

    assert record.content == {"fact": "portable-first"}


def test_decoded_memory_record_rejects_naive_created_at() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        DecodedMemoryRecord(
            memory_record_id=MemoryRecordId(uuid4()),
            source_memory_intent_id=MemoryIntentId(uuid4()),
            created_at=datetime.now(),
            correlation_id=CorrelationId(uuid4()),
            causation_id=None,
            content={"fact": "portable-first"},
        )


def test_decoded_memory_record_rejects_empty_content() -> None:
    with pytest.raises(ValueError, match="content"):
        DecodedMemoryRecord(
            memory_record_id=MemoryRecordId(uuid4()),
            source_memory_intent_id=MemoryIntentId(uuid4()),
            created_at=datetime.now(UTC),
            correlation_id=CorrelationId(uuid4()),
            causation_id=None,
            content={},
        )


def test_decoded_memory_record_content_is_immutable() -> None:
    record = make_decoded_memory_record()

    with pytest.raises(TypeError):
        record.content["fact"] = "changed"
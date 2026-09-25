from datetime import UTC, datetime

import pytest

from ayeon.contracts.common import (
    CausationId,
    CorrelationId,
    MemoryIntentId,
    MemoryRecordId,
)
from ayeon.contracts.memory_context_entry import MemoryContextEntry
from ayeon.contracts.memory_decoding import DecodedMemoryRecord


def make_decoded(
    memory_record_id: MemoryRecordId,
) -> DecodedMemoryRecord:
    return DecodedMemoryRecord(
        memory_record_id=memory_record_id,
        source_memory_intent_id=MemoryIntentId("intent-1"),
        created_at=datetime.now(UTC),
        correlation_id=CorrelationId("correlation-1"),
        causation_id=CausationId("causation-1"),
        content={"fact": "Ayeon remembers this."},
    )


def test_memory_context_entry_preserves_decoded_memory() -> None:
    record_id = MemoryRecordId("memory-1")
    decoded = make_decoded(record_id)

    entry = MemoryContextEntry(
        memory_record_id=record_id,
        decoded=decoded,
    )

    assert entry.memory_record_id == record_id
    assert entry.decoded is decoded


def test_memory_context_entry_rejects_identity_mismatch() -> None:
    decoded = make_decoded(MemoryRecordId("memory-1"))

    with pytest.raises(
        ValueError,
        match="decoded memory_record_id must match memory_record_id",
    ):
        MemoryContextEntry(
            memory_record_id=MemoryRecordId("memory-2"),
            decoded=decoded,
        )
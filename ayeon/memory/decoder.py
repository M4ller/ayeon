"""Decode durable memory payloads into typed evidence."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from ayeon.contracts.common import (
    CausationId,
    CorrelationId,
    MemoryIntentId,
    MemoryRecordId,
)
from ayeon.contracts.memory_decoding import DecodedMemoryRecord
from ayeon.memory.serialization import (
    decode_memory_content,
    encode_memory_content,
)


def decode_memory_record(payload: bytes) -> DecodedMemoryRecord:
    """Decode durable bytes without reconstructing a MemoryRecord."""

    decoded = decode_memory_content(payload)

    if encode_memory_content(decoded) != payload:
        raise ValueError(
            "durable memory payload must use canonical encoding"
        )

    expected_fields = {
        "memory_record_id",
        "source_memory_intent_id",
        "created_at",
        "correlation_id",
        "causation_id",
        "content",
    }

    if set(decoded) != expected_fields:
        raise ValueError(
            "decoded memory record fields do not match durable schema"
        )

    string_fields = (
        "memory_record_id",
        "source_memory_intent_id",
        "created_at",
        "correlation_id",
    )
    for field_name in string_fields:
        if not isinstance(decoded[field_name], str):
            raise TypeError(
                f"{field_name} must be str in durable memory payload"
            )

    raw_causation_id = decoded["causation_id"]
    if (
        raw_causation_id is not None
        and not isinstance(raw_causation_id, str)
    ):
        raise TypeError(
            "causation_id must be str or None in durable memory payload"
        )

    memory_record_id = MemoryRecordId(
        UUID(decoded["memory_record_id"])
    )
    source_memory_intent_id = MemoryIntentId(
        UUID(decoded["source_memory_intent_id"])
    )
    created_at = datetime.fromisoformat(decoded["created_at"])
    correlation_id = CorrelationId(
        UUID(decoded["correlation_id"])
    )

    causation_id = (
        None
        if raw_causation_id is None
        else CausationId(UUID(str(raw_causation_id)))
    )

    content = decoded["content"]
    if not isinstance(content, dict):
        raise TypeError("decoded memory record content must be a mapping")

    return DecodedMemoryRecord(
        memory_record_id=memory_record_id,
        source_memory_intent_id=source_memory_intent_id,
        created_at=created_at,
        correlation_id=correlation_id,
        causation_id=causation_id,
        content=content,
    )
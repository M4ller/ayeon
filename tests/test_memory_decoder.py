import json

import pytest
from test_sqlite_memory_repository import make_record

from ayeon.contracts.memory_decoding import DecodedMemoryRecord
from ayeon.memory.decoder import decode_memory_record
from ayeon.memory.serialization import encode_memory_record


def test_decode_memory_record_preserves_durable_fields() -> None:
    record = make_record()
    payload = encode_memory_record(record)

    decoded = decode_memory_record(payload)

    assert isinstance(decoded, DecodedMemoryRecord)
    assert decoded.memory_record_id == record.memory_record_id
    assert (
        decoded.source_memory_intent_id
        == record.source_memory_intent_id
    )
    assert decoded.created_at == record.created_at
    assert decoded.correlation_id == record.trace.correlation_id
    assert decoded.causation_id == record.trace.causation_id
    assert decoded.content == record.content

def test_decode_memory_record_rejects_missing_fields() -> None:
    record = make_record()
    payload = encode_memory_record(record)
    decoded = json.loads(payload)
    del decoded["source_memory_intent_id"]
    malformed = json.dumps(
        decoded,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    with pytest.raises(ValueError, match="fields"):
        decode_memory_record(malformed)


def test_decode_memory_record_rejects_unknown_fields() -> None:
    record = make_record()
    payload = encode_memory_record(record)
    decoded = json.loads(payload)
    decoded["unknown_field"] = "future-data"
    malformed = json.dumps(
        decoded,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    with pytest.raises(ValueError, match="fields"):
        decode_memory_record(malformed)

def test_decode_memory_record_rejects_non_string_identity_field() -> None:
    record = make_record()
    payload = encode_memory_record(record)
    decoded = json.loads(payload)
    decoded["memory_record_id"] = 123
    malformed = json.dumps(
        decoded,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    with pytest.raises(TypeError, match="memory_record_id"):
        decode_memory_record(malformed)

def test_decode_memory_record_rejects_naive_created_at() -> None:
    record = make_record()
    payload = encode_memory_record(record)
    decoded = json.loads(payload)
    decoded["created_at"] = "2026-09-22T18:00:00"
    malformed = json.dumps(
        decoded,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    with pytest.raises(ValueError, match="timezone-aware"):
        decode_memory_record(malformed)

def test_decode_memory_record_rejects_invalid_uuid() -> None:
    record = make_record()
    payload = encode_memory_record(record)
    decoded = json.loads(payload)
    decoded["memory_record_id"] = "not-a-uuid"
    malformed = json.dumps(
        decoded,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    with pytest.raises(ValueError):
        decode_memory_record(malformed)

def test_decode_memory_record_rejects_noncanonical_payload() -> None:
    record = make_record()
    payload = encode_memory_record(record)
    decoded = json.loads(payload)

    noncanonical = json.dumps(
        decoded,
        sort_keys=True,
    ).encode("utf-8")

    assert noncanonical != payload

    with pytest.raises(ValueError, match="canonical"):
        decode_memory_record(noncanonical)
